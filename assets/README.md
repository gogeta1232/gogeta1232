# Profile artwork

Original typography, project cards, and tool labels for this profile. The small
letter marks are labels, not official brand logos.

Regenerate from the repository root with `python scripts/build_profile_assets.py`.
The script requires Pillow and uses the Windows Arial, Consolas, and Impact fonts.
Set `PROFILE_FONT_DIR` to another directory containing those fonts if needed.

The header GIF plays once and settles on a readable final frame. The README uses
a static PNG for visitors who request reduced motion. Compact project cards are
served on narrow screens. Assets are local, so no image service or scheduled
workflow is required.
