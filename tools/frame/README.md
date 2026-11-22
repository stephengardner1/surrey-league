# Frame page

`files/frame/index.html` is the Surrey League page shown full screen on the Gracedaler kitchen Frame
(1080×1920 portrait), when the kitchen button's TV mode is set to `surrey`. Live at https://slarchive.org/frame/.

- `build.py` builds it from `files/data.json`, `files/data-women.json`, `files/fixture-times.json` and the portraits,
  using the site's own colours, club names, vests and venue names read from `files/index.html`.
- `spot.py` builds the athlete spotlight (poster card, stats, race graph). The shortlist is worked out from the data:
  Steve Gardner, the current favourites, the four runners with dogs, men with 2+ Mitchell Cups or 7+ league titles,
  and women with 3+ titles. It changes athlete every 15 minutes. Add `?spot=N` to the URL to pin one.
- `photos.json` is the rotating photo slot. It is edited by hand after each match: `pos` sets the vertical crop
  so the main subject's eyes sit a third of the way down.
- The "Frame page" workflow rebuilds it when the results change and hourly.

Run locally: `cd tools/frame && python3 build.py` (needs Node and `pip install fonttools`).
