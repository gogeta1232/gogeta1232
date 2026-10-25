"""Build the profile's original typography and motion assets with Pillow.

Run: python scripts/build_profile_assets.py
Requires Pillow. Windows fonts are used by default; PROFILE_FONT_DIR can override.
The GIF plays once, then rests on the finished composition.
"""

import math
import os
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
FONTS = Path(os.environ.get('PROFILE_FONT_DIR', 'C:/Windows/Fonts'))
INK = '#141519'
PAPER = '#f3f1e9'
BLUE = '#364cff'
LIME = '#d9fb6b'


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def tracked(draw, pos, text, face, fill, spacing=3):
    x, y = pos
    for letter in text:
        draw.text((x, y), letter, font=face, fill=fill, anchor='lt')
        x += draw.textlength(letter, font=face) + spacing


def header(frame):
    image = Image.new('RGB', (1280, 438), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, 1277, 435), outline=INK, width=5)
    draw.rectangle((0, 0, 1279, 48), fill=INK)
    tracked(draw, (30, 16), 'LAKSHYA / ALSO EMBER', font('consolab.ttf', 17), PAPER, 2)
    tracked(draw, (887, 16), 'DEVELOPMENT + EDITING', font('consola.ttf', 16), PAPER, 1)

    # Name stays readable in every frame; motion belongs to the editing motif.
    name = Image.new('RGBA', (1100, 260))
    name_draw = ImageDraw.Draw(name)
    name_draw.text((0, 0), 'LAKSHYA', font=font('impact.ttf', 242), fill=INK, anchor='lt')
    box = name.getbbox()
    name = name.crop(box).resize((918, 223), Image.Resampling.LANCZOS)
    image.paste(name, (29, 77), name)

    cx, cy, radius = 1120, 186, 97
    draw.ellipse((cx-radius+8, cy-radius+8, cx+radius+8, cy+radius+8), fill=INK)
    draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=BLUE, outline=INK, width=4)
    angle = min(frame / 44, 1) * math.tau
    for index in range(4):
        a = angle + index * math.pi / 2
        px, py = cx + math.cos(a) * 57, cy + math.sin(a) * 57
        draw.ellipse((px-17, py-17, px+17, py+17), fill=PAPER, outline=INK, width=3)
    draw.ellipse((cx-15, cy-15, cx+15, cy+15), fill=LIME, outline=INK, width=3)
    tracked(draw, (1047, 309), 'MAKE. CUT.', font('consolab.ttf', 18), INK, 1)
    tracked(draw, (29, 327), 'DISCORD BOTS / WEB INTERFACES / VIDEO EDITS', font('consolab.ttf', 21), INK, 1)

    # A short original timeline animation, not a simulated live-status widget.
    draw.rectangle((4, 377, 1275, 433), fill=BLUE)
    tracked(draw, (30, 395), 'CODE MEETS THE EDIT BAY.', font('consolab.ttf', 19), PAPER, 1)
    for start, end in [(784, 860), (867, 968), (975, 1030), (1037, 1155), (1162, 1247)]:
        draw.rectangle((start, 397, end, 414), fill=PAPER)
    playhead = int(785 + min(frame / 44, 1) * 460)
    draw.line((playhead, 387, playhead, 425), fill=LIME, width=4)
    draw.polygon([(playhead-7, 385), (playhead+7, 385), (playhead, 393)], fill=LIME)
    return image


frames = [header(frame) for frame in range(49)]
frames[0].save(ASSETS / 'header.gif', save_all=True, append_images=frames[1:],
               duration=[80] * 48 + [1000], optimize=True, disposal=1)
frames[-1].save(ASSETS / 'header-static.png', optimize=True)


def svg_file(filename, width, height, body, title):
    text = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<style>text{{font-family:Arial,Helvetica,sans-serif}}.mono{{font-family:Consolas,'Liberation Mono',monospace}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
{body}</svg>'''
    (ASSETS / filename).write_text(text, encoding='utf-8')


for filename, title, label, mark, color, width in [
    ('typescript.svg', 'TypeScript', 'TypeScript', 'TS', '#3178c6', 151),
    ('react.svg', 'React', 'React', 'R', '#087ea4', 111),
    ('node.svg', 'Node.js', 'Node.js', 'N', '#43853d', 128),
    ('html-css.svg', 'HTML and CSS', 'HTML / CSS', '<>', '#b4451c', 155),
    ('after-effects.svg', 'Adobe After Effects', 'After Effects', 'Ae', '#6655df', 180),
    ('premiere.svg', 'Adobe Premiere Pro', 'Premiere Pro', 'Pr', '#6655df', 176),
]:
    svg_file(filename, width, 43, f'''
<rect x="3" y="3" width="{width-3}" height="40" fill="{INK}"/>
<rect x="1" y="1" width="{width-5}" height="37" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>
<rect x="1" y="1" width="38" height="37" fill="{color}" stroke="{INK}" stroke-width="2"/>
<text x="20" y="25" text-anchor="middle" fill="white" font-size="15" font-weight="700">{escape(mark)}</text>
<text x="49" y="25" fill="{INK}" font-size="14" font-weight="700">{escape(label)}</text>''', title)


def card(filename, title, subtitle, tag, accent, motif):
    svg_file(filename, 600, 224, f'''
<rect x="9" y="9" width="591" height="215" fill="{INK}"/>
<rect x="2" y="2" width="587" height="211" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>
<rect x="2" y="2" width="587" height="42" fill="{accent}"/>
<text class="mono" x="24" y="29" fill="{PAPER if accent == BLUE else INK}" font-size="17" font-weight="700">{escape(tag)}</text>
<text x="24" y="116" fill="{INK}" font-size="55" font-weight="900" letter-spacing="-2">{escape(title)}</text>
<text x="25" y="154" fill="{INK}" font-size="21">{escape(subtitle)}</text>
<path d="M25 180 H562" stroke="{INK}" stroke-width="2"/>
<text class="mono" x="25" y="201" fill="{INK}" font-size="14">{escape(motif)}</text>
<path d="M531 75 H561 V105 M560 76 L526 110" stroke="{INK}" stroke-width="5" fill="none"/>
''', title + ' — ' + subtitle)


card('bolt.svg', 'BOLT-OS', 'Moderation, built around control.', 'DISCORD / TYPESCRIPT', BLUE, 'SAPPHIRE + DISCORD.JS + MONGODB')
card('docs.svg', 'BOLT DOCS', 'A clearer way into the commands.', 'WEB / REACT', BLUE, 'REACT + VITE + TYPESCRIPT')

for filename, label in [('bolt-compact.svg', 'BOLT-OS'), ('docs-compact.svg', 'BOLT DOCS')]:
    svg_file(filename, 400, 165, f'''
<rect x="8" y="8" width="392" height="157" fill="{INK}"/>
<rect x="2" y="2" width="387" height="151" fill="{PAPER}" stroke="{INK}" stroke-width="4"/>
<rect x="2" y="2" width="387" height="24" fill="{BLUE}"/>
<text x="20" y="105" fill="{INK}" font-size="59" font-weight="900" letter-spacing="-2">{label}</text>
<path d="M21 127 H367" stroke="{INK}" stroke-width="3"/>
''', label)

for path in sorted(ASSETS.iterdir()):
    print(f'{path.name}: {path.stat().st_size:,} bytes')
