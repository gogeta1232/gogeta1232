# Compact projects

The README project block is generated from public repositories by
`python scripts/update_projects.py`. Bolt is pinned, its documentation is a
link in the same entry, and new projects use the same compact format. No new
artwork is required. `projects.json` controls pinned/excluded repositories,
descriptions, links, and the maximum of six entries. Extra entries receive one
More repositories link. Only public, owned, non-fork, active repositories qualify.

The published Refresh projects workflow is **manual only**. It has no schedule
or push trigger. Choosing Run workflow authorizes it to refresh and commit only
this README block.
There is no automatic publishing on repository creation.

One API request reads at most 100 recently pushed repositories, with a 15-second
timeout and a 2 MiB response cap. No retries, cache, database, server, or paid
service is introduced. Failure leaves the README unchanged. Output is bounded
to six entries; no timestamps or unchanged commits create history churn. The
workflow has a three-minute job limit and a single concurrency group.

`--from-json path.json` allows local review against a saved public API response.
`--save-json path.json` saves that response when diagnosing an update. These
options never publish. Hand-authored content outside the markers is preserved.

## Animation review

The current v3 header contains 80 distinct frames over ten seconds. The live
README uses direct lossless animated WebP img tags for the header, flame, robot,
clapperboard, and star divider, following royalrizen's animated WebP example.
GitHub's rendered markup leaves these as plain images instead of tagging them
as GIFs for playback controls. No custom player is embedded. Platform rendering
may change. Earlier picture/source wrappers that selected still images remain
removed; static alternatives and GIF masters are retained as separate files.

`python scripts/build_animated_webp.py` rebuilds the five WebP files and verifies
lossless decoded frames, identical timing, and infinite loops against the GIFs.
`assets/pixel-profile/animated-webp-qa.json` records those results. File and HTML
verification does not establish playback in a particular viewer's browser.
