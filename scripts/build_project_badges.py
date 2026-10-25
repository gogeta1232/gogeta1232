"""Compact pixel labels for the featured project; original logos stay intact."""
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/pixel-profile'
font=TTFont(OUT/'Silkscreen-Regular.ttf')
glyphs,cmap=font.getGlyphSet(),font.getBestCmap()
units=font['head'].unitsPerEm

def label(value,x,y,size,color):
    cursor=0;paths=[]
    for character in value:
        glyph=glyphs[cmap[ord(character)]];pen=SVGPathPen(glyphs);glyph.draw(pen)
        paths.append(f'<path transform="translate({cursor},0)" d="{pen.getCommands()}"/>');cursor+=glyph.width
    return f'<g fill="{color}" transform="translate({x},{y}) scale({size/units},-{size/units})">'+''.join(paths)+'</g>'

for filename,value,width,color in [('project-bolt-label-v3.svg','BOLT-OS',130,'#bca3ee'),('project-docs-label-v3.svg','DOCS',90,'#84cdd2')]:
    body=f'<path d="M5 1H{width-5}V5H{width-1}V29H{width-5}V33H5V29H1V5H5Z" fill="#171b30" stroke="{color}"/>'
    if value=='BOLT-OS':
        original=ET.parse(ROOT/'assets/dark-profile/icons/github.svg').getroot()
        children=''.join(ET.tostring(deepcopy(child),encoding='unicode') for child in original)
        body+=f'<svg x="9" y="9" width="16" height="16" viewBox="0 0 24 24" fill="{color}">{children}</svg>'
    else:
        body+=f'<path d="M9 9H20V11H23V25H12V23H9ZM12 12V20H19M12 16H19" fill="none" stroke="{color}" stroke-width="2"/>'
    body+=label(value,32,23,16,color)
    (OUT/filename).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="34" viewBox="0 0 {width} 34" role="img"><title>{value}</title>{body}</svg>',encoding='utf-8')
print('Compact Bolt and Docs labels built.')
