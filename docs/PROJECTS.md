# Compact projects

The README project block is generated from public repositories by
`python scripts/update_projects.py`. Bolt is pinned, its documentation is a
link in the same entry, and new projects use the same compact format. No new
artwork is required. `projects.json` controls pinned/excluded repositories,
descriptions, links, and the maximum of six entries. Extra entries receive one
More repositories link. Only public, owned, non-fork, active repositories qualify.

The prepared Refresh projects workflow is **manual only**. It has no schedule,
push trigger, or live activation in this unpublished draft. Once published,
choosing Run workflow authorizes it to refresh and commit only this README block.
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

The header GIF is 64 frames over eight seconds. The saved T3 attachment was
inspected: its inlined image retains all 64 GIF frames. The T3 headless preview
reported reduced motion enabled and therefore selected the README's PNG source.
That observation does not establish the user's OS preference.

The current local review page has an explicit frame player built from those GIF
frames, a Play control, and a native-video fallback. It is a preview tool; the
GitHub README continues to use GIFs and reduced-motion picture sources. Native
pixel rendering was checked in the preview, but the collaborative browser's
snapshot/click checks timed out, so live T3 client playback is not claimed as
verified. An eight-second, 64-frame MP4 was decoded successfully for review.
