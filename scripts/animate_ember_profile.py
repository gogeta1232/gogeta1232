"""Build local Ember animation assets from preserved ImageGen masters.

Pillow packages the generated sprite frames and renders localized animation
layers over the renamed master. The generated originals remain untouched.
Requires Pillow and numpy. Does not commit, upload, or push.
"""
from copy import deepcopy
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/pixel-profile'
ICONS = ROOT / 'assets/dark-profile/icons'
FRAMES = 64
DURATION = 125
W, H = 1024, 356

with Image.open(OUT / 'ember-studio-source-v2.png') as image:
    base = image.convert('RGB').resize((W, H), Image.Resampling.NEAREST)
base.save(OUT / 'ember-studio-static-v2.png', optimize=True)
pixels = np.asarray(base).astype(np.float32)
yy, xx = np.indices((H, W))

# Isolate the bright lavender letter faces; the wall and poster stay fixed.
name_mask = ((xx >= 77) & (xx <= 367) & (yy >= 138) & (yy <= 194)
             & (pixels[:, :, 0] > 105) & (pixels[:, :, 1] > 75)
             & (pixels[:, :, 2] > pixels[:, :, 0] + 8))
lamp_mask = ((xx > 855) & (yy > 147) & (yy < 190)
             & (pixels[:, :, 0] > 160) & (pixels[:, :, 1] > 95)
             & (pixels[:, :, 2] < 170))


def frame(index):
    t = index / FRAMES
    rgb = pixels.copy()
    # One soft pass over the name in each eight-second loop. No flashing.
    sweep = (t - .1) / .40
    if 0 <= sweep <= 1:
        center = 40 + sweep * 380
        highlight = np.maximum(0, 1 - abs(xx - center) / 27) * name_mask
        rgb += highlight[:, :, None] * np.array([37, 39, 28], dtype=np.float32)
    # Warm material highlights breathe gently, without changing the room exposure.
    rgb += lamp_mask[:, :, None] * (math.sin(t * math.tau) * 7)
    image = Image.fromarray(np.uint8(np.clip(rgb, 0, 255)))
    draw = ImageDraw.Draw(image)

    # Stable stars, distinct slow cycles. No movement of the skyline/window.
    for x, y, offset in [(584, 53, 0), (680, 37, .3), (791, 43, .65)]:
        amount = (math.sin((t + offset) * math.tau) + 1) / 2
        color = tuple(int(a + (b-a) * amount) for a, b in zip((67, 66, 126), (201, 190, 242)))
        draw.rectangle((x, y, x+1, y+1), fill=color)
        if amount > .86:
            draw.point((x-1, y), fill=(134, 124, 195))
            draw.point((x+2, y+1), fill=(134, 124, 195))

    # The editor loops through the visible timeline; the code caret blinks.
    playhead = int(707 + t * 118)
    draw.line((playhead, 198, playhead, 221), fill=(151, 247, 223), width=1)
    draw.polygon([(playhead-2, 196), (playhead+2, 196), (playhead, 199)], fill=(184, 251, 232))
    if index % 12 < 7:
        draw.rectangle((608, 205, 609, 208), fill=(84, 201, 193))

    # Two wisps over the existing mug. Their small stepped paths suit the pixels.
    for offset in [0, .48]:
        phase = (t * 2 + offset) % 1
        rise = int(phase * 15)
        x = 523 + int(math.sin(phase * math.tau) * 2)
        y = 232 - rise
        strength = math.sin(phase * math.pi) * .45
        if strength > .1:
            for dx, dy in [(0, 0), (0, -1), (1, -2), (1, -3)]:
                px, py = x+dx, y+dy
                original = image.getpixel((px, py))
                draw.point((px, py), fill=tuple(int(a+(b-a)*strength) for a, b in zip(original, (179, 165, 198))))
    return image


frames = [frame(index) for index in range(FRAMES)]
# One shared palette prevents the whole scene from shimmering between frames.
palette_source = Image.new('RGB', (W, H+16))
palette_source.paste(base)
swatches = ImageDraw.Draw(palette_source)
for n, color in enumerate([(214, 199, 255), (163, 143, 229), (151, 247, 223), (84, 201, 193), (255, 220, 133), (67, 66, 126), (134, 124, 195)]):
    swatches.rectangle((n*120, H, (n+1)*120-1, H+15), fill=color)
palette = palette_source.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
gif_frames = [image.quantize(palette=palette, dither=Image.Dither.NONE) for image in frames]
gif_frames[0].save(OUT / 'ember-studio-loop-v2.gif', save_all=True,
                   append_images=gif_frames[1:], duration=[120, 130]*(FRAMES//2), loop=0,
                   optimize=True, disposal=1)

# An inspection sheet records phases of the actual animated output.
sheet = Image.new('RGB', (W, H*4))
for row, index in enumerate([0, 12, 28, 48]):
    sheet.paste(frames[index], (0, row*H))
sheet.save(OUT / 'animation-contact-sheet-v2.jpg', quality=90)


def save_transparent_gif(name, frames, durations):
    """Use a shared palette and a reserved transparent index for each sprite."""
    atlas = Image.new('RGB', (128*len(frames), 128))
    for index, image in enumerate(frames):
        atlas.paste(image.convert('RGB'), (index*128, 0))
    palette = atlas.quantize(colors=63, dither=Image.Dither.NONE)
    colors = [0, 0, 0] + palette.getpalette()[:63*3]
    colors += [0] * (768-len(colors))
    indexed = []
    for image in frames:
        q = image.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
        values = np.asarray(q).astype(np.uint8) + 1
        values[np.asarray(image.getchannel('A')) < 128] = 0
        encoded = Image.fromarray(values, mode='P')
        encoded.putpalette(colors)
        indexed.append(encoded)
    indexed[0].save(OUT / (name+'.gif'), save_all=True, append_images=indexed[1:],
                    loop=0, duration=durations, transparency=0, background=0,
                    disposal=2, optimize=False)
    frames[0].save(OUT / (name+'-static.png'), optimize=True)


with Image.open(OUT / 'accent-atlas-source-v2.png') as atlas_source:
    atlas = atlas_source.convert('RGBA')
    cell_width = atlas.width // 4
    # Shared bands follow the transparent gutters, not an assumed square grid.
    rows = [('robot-idle-v2', 45, 386, [1600, 220, 160, 1800]),
            ('clapper-v2', 405, 710, [1800, 220, 300, 220]),
            ('ember-flame-v2', 728, 1038, [280, 280, 280, 280])]
    for name, top, bottom, durations in rows:
        outputs = []
        for column in range(4):
            crop = atlas.crop((column*cell_width, top, (column+1)*cell_width, bottom))
            shared = Image.new('RGBA', (cell_width, cell_width))
            shared.alpha_composite(crop, (0, (cell_width-crop.height)//2))
            # Fixed shared bounds preserve animation scale and subject position.
            sprite = shared.resize((32, 32), Image.Resampling.NEAREST)
            outputs.append(sprite.resize((128, 128), Image.Resampling.NEAREST))
        save_transparent_gif(name, outputs, durations)

# Framing is code-native; the enclosed upstream brand paths are preserved.
for name in ['typescript', 'javascript', 'react', 'html5', 'css3', 'nodejs', 'mongodb', 'aftereffects', 'premierepro']:
    source = ET.parse(ICONS / (name+'.svg')).getroot()
    children = ''.join(ET.tostring(deepcopy(child), encoding='unicode') for child in source)
    viewbox = source.attrib.get('viewBox', '0 0 128 128')
    content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img"><title>{name}</title>
<path d="M8 2H56V8H62V56H56V62H8V56H2V8H8Z" fill="#151a2c" stroke="#625783" stroke-width="2"/>
<path d="M10 6H54M6 10V54" stroke="#3b3657" stroke-width="2"/>
<rect x="54" y="54" width="4" height="4" fill="#a493cb"/>
<svg x="13" y="13" width="38" height="38" viewBox="{viewbox}">{children}</svg></svg>'''
    (OUT / ('tool-'+name+'-v2.svg')).write_text(content, encoding='utf-8')

report = {'header': {'frames': FRAMES, 'duration_ms': FRAMES*DURATION,
                      'size': [W, H], 'gif_bytes': (OUT/'ember-studio-loop-v2.gif').stat().st_size,
                      'name_mask_pixels': int(name_mask.sum()),
                      'lamp_mask_pixels': int(lamp_mask.sum())},
          'effects': ['Ember lettering highlight sweep', 'slow star twinkles', 'warm lamp breathing',
                      'editor timeline playhead', 'code caret', 'small mug steam'],
          'sprites': ['robot-idle-v2', 'clapper-v2', 'ember-flame-v2'],
          'sprite_logical_size': 32,
          'framed_brand_icons': 9,
          'publishing': 'Local draft only; user approval is required.'}
(OUT / 'animation-build-v2.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
# Let the preview's pause control and reduced-motion picture freeze the divider.
import re
divider = (OUT / 'pixel-divider.svg').read_text(encoding='utf-8')
(OUT / 'pixel-divider-static-v2.svg').write_text(re.sub(r'<style>.*?</style>', '', divider, flags=re.S), encoding='utf-8')
print(json.dumps(report, indent=2))
