# Ember pixel studio artwork

The current profile was approved for publication. Future changes still require
review before publishing, as described in the root AGENTS.md.

The header is ember-studio-loop-v3.gif: 80 frames over ten seconds, with a shared
192-color palette and a retained static alternative file. It includes a bright
name sweep, finishing sparkle, lamp dimming, staggered skyline lights, headphone
music notes, chair sway, a code caret, an editing playhead, stars, and steam.

Built-in ImageGen produced the chair-free room plate and transparent chair layer.
Both original layers and their exact prompts are preserved in generation-v3.json.
Earlier source masters and generation records are retained for provenance. The
small robot, clapperboard, and flame GIFs use the generated v2 sprite atlas with
fixed shared bounds and retained static files.

The live README embeds the actual GIFs directly with img tags. It does not use
picture/source rules that could substitute a PNG or SVG. The star divider is
pixel-divider-v4.gif, rebuilt with `python scripts/build_gif_divider.py`; the
earlier animated SVG remains editable source. GitHub's account-level Autoplay
animated images preference may still pause GIF playback for an individual viewer.

The original tool and social marks are preserved from Devicon and Simple Icons.
Their sources and licenses are in ../dark-profile. Pixel frames and labels use
Silkscreen, with its SIL Open Font License preserved here. Premiere Pro is not
displayed; the current editing tool is After Effects.

Rebuild the current header with `python scripts/animate_ember_studio_v3.py`
(Pillow and numpy), the sprite/icon assets with
`python scripts/animate_ember_profile.py`, and the compact project labels with
`python scripts/build_project_badges.py` (fontTools). Run these from the repository
root. Only the v3 header is referenced by the README.

animation-build-v3.json and animation-qa-v3.json record the actual dimensions,
frame duration, file size, changed regions, and checks. No running server,
image API, paid hosting, or scheduled workflow is required to display the profile.
