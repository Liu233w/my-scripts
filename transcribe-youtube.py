#!/usr/bin/python3

import sys
import requests
import json
import time

def fetch_transcription(video_url, lang):
    try:
        data = {"videoUrl": video_url, "langCode": lang}
        if not lang:
            del data['langCode']

        response = requests.post(
            'https://tactiq-apps-prod.tactiq.io/transcript',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )

        if response.status_code in [419, 415] and lang:
            # langCode not supported, switch to default language
            return fetch_transcription(video_url, None)

        if response.status_code == 429:
            # too many requests
            time.sleep(30)
            return fetch_transcription(video_url, lang)

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch transcription data: {e}", file=sys.stderr)
        sys.exit(1)

def format_time(seconds):
    seconds = float(seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"[{hours:02}:{minutes:02}:{seconds:02}]"

def main(video_url):
    transcription = fetch_transcription(video_url, 'zh')

    for caption in transcription.get("captions", []):
        start = caption.get("start", "0")
        text = caption.get("text", "")
        formatted_time = format_time(start)
        print(f"{formatted_time} {text}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <video-url>".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    video_url = sys.argv[1]
    main(video_url)
