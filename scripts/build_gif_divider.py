"""A real animated GIF for the existing code-native pixel-star divider."""
import math
from pathlib import Path
from PIL import Image, ImageDraw

OUT=Path(__file__).resolve().parents[1]/'assets/pixel-profile'
WIDTH,HEIGHT=600,24
frames=[]
for index in range(24):
    image=Image.new('P',(WIDTH,HEIGHT),0)
    palette=[0,0,0,75,72,107]
    # Four tonal steps per star; index zero is reserved for transparency.
    for color in [(179,154,232),(108,188,196),(179,154,232)]:
        for level in [.35,.55,.78,1.0]:palette.extend(int(value*level) for value in color)
    image.putpalette(palette+[0]*(768-len(palette)))
    draw=ImageDraw.Draw(image)
    draw.line((0,12,276,12),fill=1,width=2)
    draw.line((324,12,599,12),fill=1,width=2)
    for star,(x,y) in enumerate([(285,8),(297,4),(309,8)]):
        phase=(index/24+star/3)%1
        step=min(3,int((.5+.5*math.sin(phase*math.tau))*4))
        color=2+star*4+step
        draw.polygon([(x+2,y),(x+5,y),(x+5,y+4),(x+9,y+4),(x+9,y+7),(x+5,y+7),(x+5,y+11),(x+2,y+11),(x+2,y+7),(x-2,y+7),(x-2,y+4),(x+2,y+4)],fill=color)
    frames.append(image)
frames[0].save(OUT/'pixel-divider-v4.gif',save_all=True,append_images=frames[1:],duration=200,loop=0,transparency=0,background=0,disposal=2,optimize=False)
print('Animated GIF divider created.')
