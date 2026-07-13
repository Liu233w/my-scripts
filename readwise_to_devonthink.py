#!/usr/bin/env python3
"""
readwise_to_devonthink.py

Fetch documents from your Readwise Reader library and send their URLs to
DEVONthink -- as bookmarks (default), or as full web archive / PDF / Markdown
captures of the pages.

Requirements
------------
- macOS with DEVONthink 3 or 4 installed
- Python 3.8+ (standard library only, nothing to install)
- A Readwise access token from https://readwise.io/access_token

Setup
-----
    export READWISE_TOKEN="xxxxxxxxxxxxxxxx"
    chmod +x readwise_to_devonthink.py

Examples
--------
    # Send your whole Reader library to DEVONthink as bookmarks
    ./readwise_to_devonthink.py

    # Only archived items, captured as full web archives
    ./readwise_to_devonthink.py --location archive --as webarchive

    # Into a specific database and group
    ./readwise_to_devonthink.py --database "Research" --group "/Readwise/Articles"

    # Preview without touching DEVONthink
    ./readwise_to_devonthink.py --dry-run

    # Incremental sync (only items added/updated since the last run)
    ./readwise_to_devonthink.py --since-last-run
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://readwise.io/api/v3/list/"
STATE_FILE = Path.home() / ".readwise_devonthink_state.json"

# Reader rows whose category marks them as annotations, not documents
ANNOTATION_CATEGORIES = {"highlight", "note"}

# AppleScript run via `osascript -` with arguments:
#   1: URL   2: title   3: kind (bookmark|webarchive|pdf|markdown)
#   4: group path   5: database name ("" = Global Inbox)
ADD_SCRIPT = '''
on run argv
    set theURL to item 1 of argv
    set theTitle to item 2 of argv
    set theKind to item 3 of argv
    set theGroupPath to item 4 of argv
    set theDatabase to item 5 of argv
    tell application id "DNtp"
        if theDatabase is "" then
            set theDB to inbox
        else
            set theDB to database theDatabase
        end if
        -- skip if a record with this URL already exists in the database
        set existing to lookup records with URL theURL in theDB
        if (count of existing) > 0 then return "duplicate"
        set theGroup to create location theGroupPath in theDB
        if theKind is "bookmark" then
            create record with {name:theTitle, type:bookmark, URL:theURL} in theGroup
        else if theKind is "webarchive" then
            create web document from theURL name theTitle in theGroup
        else if theKind is "pdf" then
            create PDF document from theURL name theTitle in theGroup
        else if theKind is "markdown" then
            create Markdown from theURL name theTitle in theGroup
        end if
        return "added"
    end tell
end run
'''


def fetch_documents(token, location=None, category=None, updated_after=None):
    """Yield documents from the Readwise Reader API, following pagination."""
    cursor = None
    while True:
        params = {"withHtmlContent": "false"}
        if location:
            params["location"] = location
        if category:
            params["category"] = category
        if updated_after:
            params["updatedAfter"] = updated_after
        if cursor:
            params["pageCursor"] = cursor

        url = API_URL + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Authorization": f"Token {token}"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limited (Reader allows ~20 req/min)
                wait = int(e.headers.get("Retry-After", "60") or "60")
                print(f"  Rate limited by Readwise, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            if e.code == 401:
                sys.exit("Error: Readwise rejected the token (401). Check READWISE_TOKEN.")
            raise

        yield from data.get("results", [])
        cursor = data.get("nextPageCursor")
        if not cursor:
            break


def send_to_devonthink(url, title, kind, group, database):
    """Create one record in DEVONthink via AppleScript. Returns 'added' or 'duplicate'."""
    result = subprocess.run(
        ["osascript", "-", url, title, kind, group, database],
        input=ADD_SCRIPT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "osascript failed")
    return result.stdout.strip()


def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(state):
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except OSError as e:
        print(f"Warning: could not write state file: {e}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(
        description="Send Readwise Reader library URLs to DEVONthink."
    )
    p.add_argument("--token", default=os.environ.get("READWISE_TOKEN"),
                   help="Readwise access token (or set READWISE_TOKEN)")
    p.add_argument("--location", choices=["new", "later", "shortlist", "archive", "feed"],
                   help="Only sync items in this Reader location (default: all)")
    p.add_argument("--category",
                   choices=["article", "email", "rss", "pdf", "epub", "tweet", "video"],
                   help="Only sync items of this category (default: all documents)")
    p.add_argument("--as", dest="kind", default="bookmark",
                   choices=["bookmark", "webarchive", "pdf", "markdown"],
                   help="How to store each item in DEVONthink (default: bookmark). "
                        "webarchive/pdf/markdown re-download the page content.")
    p.add_argument("--url-type", default="source", choices=["source", "reader"],
                   help="Send the original source URL (default) or the "
                        "read.readwise.io Reader URL")
    p.add_argument("--group", default="/Readwise",
                   help="DEVONthink group path, created if missing (default: /Readwise)")
    p.add_argument("--database", default="",
                   help="DEVONthink database name (default: Global Inbox)")
    p.add_argument("--since-last-run", action="store_true",
                   help="Only fetch items added/updated since this script last ran")
    p.add_argument("--limit", type=int, default=0,
                   help="Stop after N items (useful for testing)")
    p.add_argument("--dry-run", action="store_true",
                   help="List what would be sent without touching DEVONthink")
    args = p.parse_args()

    if not args.token:
        sys.exit("Error: no token. Set READWISE_TOKEN or pass --token.\n"
                 "Get one at https://readwise.io/access_token")

    if sys.platform != "darwin" and not args.dry_run:
        sys.exit("Error: DEVONthink automation requires macOS. Use --dry-run elsewhere.")

    state = load_state()
    updated_after = state.get("last_run") if args.since_last_run else None
    if args.since_last_run and not updated_after:
        print("No previous run recorded; doing a full sync this time.")
    run_started = datetime.now(timezone.utc).isoformat()

    added = duplicates = skipped = errors = 0
    processed = 0

    print(f"Fetching Readwise Reader library"
          f"{' (location: ' + args.location + ')' if args.location else ''}"
          f"{' updated after ' + updated_after if updated_after else ''}...")

    for doc in fetch_documents(args.token, args.location, args.category, updated_after):
        # Reader returns highlights/notes as child rows -- skip them
        if doc.get("parent_id") or doc.get("category") in ANNOTATION_CATEGORIES:
            continue

        url = doc.get("source_url") if args.url_type == "source" else doc.get("url")
        url = url or doc.get("url") or doc.get("source_url")
        if not url:
            skipped += 1
            continue

        title = (doc.get("title") or "").strip() or url

        if args.limit and processed >= args.limit:
            break
        processed += 1

        if args.dry_run:
            print(f"  [dry-run] {title}  ->  {url}")
            continue

        try:
            outcome = send_to_devonthink(url, title, args.kind, args.group, args.database)
        except RuntimeError as e:
            errors += 1
            print(f"  ERROR: {title}: {e}", file=sys.stderr)
            continue

        if outcome == "duplicate":
            duplicates += 1
            print(f"  = already in DEVONthink: {title}")
        else:
            added += 1
            print(f"  + added: {title}")

    if not args.dry_run:
        state["last_run"] = run_started
        save_state(state)

    print(f"\nDone. {added} added, {duplicates} duplicates skipped, "
          f"{skipped} without URLs, {errors} errors."
          f"{' (dry run: ' + str(processed) + ' items previewed)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
