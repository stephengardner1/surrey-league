# Retired features

Taken off slarchive.org (and so the app) on 20 November 2026 at Steve's request. The code is kept here so it can be brought back. Nothing in this folder is served by the site.

Last commit with all three live: `163d93ad6d84ae8009749615b1ec805b809c24ef`

| Feature | File here | How it was reached |
|---|---|---|
| Pub quiz | `pub-quiz.jsx` | Only by address: `/#quiz`. No link pointed to it. |
| Ask the archive | `ask-the-archive.jsx` | Not reachable. The page existed in the code but had no route. |
| Submit results | `submit-results.jsx` | Three links: "Know the original results?" and "Submit more results" on race pages, and "Submit results" under partial season tables. |

## To restore one

1. Paste its component back into `files/index.html` (near `OriginStoryView`).
2. Re-add its route in the main render, e.g. `{view.type==='quiz'&&<PubQuizView setView={setView}/>}`.
3. For the quiz, re-add the `quiz` cases in the address parsing, the address writing and the page title list.
4. For Submit results, re-add the links. The exact markup is in the commit above.

Or simply look at the commit above, which has everything in place.
