`
Extract information of all bookmarks with a tag

Inputs (environment variables):
ACCESS_TOKEN
CATEGORY: the category to look for
SEARCH_TEXT: search text, can include tags
`;

import "https://deno.land/x/dotenv/load.ts";
import { assert } from "https://deno.land/std@0.102.0/testing/asserts.ts";
import isString from "https://deno.land/x/lodash@4.17.15-es/isString.js";
import { writeJson } from "https://deno.land/x/jsonfile/mod.ts";

const ACCESS_TOKEN = getEnv("ACCESS_TOKEN");
const COLLECTION_ID = getEnv("COLLECTION_ID");
const SEARCH_TEXT = `"#fallout 4"`;

console.error(`read envs:
ACCESS_TOKEN: ${ACCESS_TOKEN}
COLLECTION_ID: ${COLLECTION_ID}
SEARCH_TEXT: ${SEARCH_TEXT}
`);

async function main() {
  const raindrops = await fetchRaindrops();
  writeJson("bookmark.json", raindrops, { spaces: 2 });
  console.error(`Total entries: ${raindrops.length}`);
  console.log(buildHtmlOutput(raindrops));
}

async function fetchRaindrops(): Promise<Entry[]> {
  let result: Entry[] = [];
  let page = 0;
  while (true) {
    const response = await fetch(
      `https://api.raindrop.io/rest/v1/raindrops/${COLLECTION_ID}?search=${
        encodeURIComponent(SEARCH_TEXT)
      }&perpage=50&page=${page}`,
      {
        headers: {
          Authorization: `Bearer ${ACCESS_TOKEN}`,
        },
      },
    );
    const json = await response.json() as unknown as { items: Entry[] };
    console.error(`fetched ${json.items.length} bookmarks`)

    if (json.items.length <= 0) {
      break;
    }

    result = result.concat(json.items);
    ++page;
  }

  return result;
}

function buildHtmlOutput(raindrops: Entry[]) {
  let result = "";
  raindrops.forEach((e) => {
    result += buildBookmarkEntryHtml(e);
  });
  return result;
}

function buildBookmarkEntryHtml(entry: Entry) {
  // return `
  // <div style="font-family: Verdana; font-size: 13px;" id="previewBody" class=" ">
  //   <table style="table-layout:auto;border-collapse:collapse;margin-bottom:24px;">
  //     <tr style="vertical-align:top;">
  //       <td style="padding-top:9px;" width="112">
  //         <img id="bookmarkThumbnail" src="${entry.cover}" alt="thumbnail" width="112">
  //       </td>
  //       <td style="padding-left:16px;">
  //         <table>
  //           <tr><td>
  //             <h2 style="margin:0;margin-bottom:13px;">${entry.title}</h2>
  //           </td></tr>
  //           <tr><td style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-bottom:13px;">
  //             <a tabindex="-1" href="${entry.link}" target="_blank" title="${entry.link}">${entry.link}</a>
  //           </td></tr>
  //           <tr><td style="word-wrap:break-word;">${entry.excerpt}</td></tr>
  //         </table>
  //       </td>
  //     </tr>
  //   </table>
  // </div>
  // `;

  return `<h3><A HREF="${entry.link}">${entry.title}</A></h3>
  <p>${entry.excerpt}</p>
  <br>
`
}

interface Entry {
  title: string;
  link: string;
  excerpt: string;
  cover: string;
  created: string;
  lastUpdate: string;
  tags: string[];
}

function getEnv(name: string) {
  const result = Deno.env.get(name) as string;
  assert(isString(result));
  return result;
}

await main();
