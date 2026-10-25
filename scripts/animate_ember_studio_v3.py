"""Build the brighter, living studio from preserved ImageGen animation layers.

Requires Pillow and numpy. Offline asset build only; never publishes.
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/pixel-profile'
W, H, COUNT = 1024, 356, 80
with Image.open(OUT/'studio-clean-plate-v3.png') as source:
    background=source.convert('RGB').resize((W,H),Image.Resampling.NEAREST)
with Image.open(OUT/'chair-layer-v3.png') as source:
    chair=source.convert('RGBA').resize((W,H),Image.Resampling.NEAREST)
chair.putalpha(chair.getchannel('A').point(lambda value: 0 if value < 16 else value))
pixels=np.asarray(background).astype(np.float32)
yy,xx=np.indices((H,W))
name=((xx>=77)&(xx<=367)&(yy>=138)&(yy<=195)&(pixels[:,:,0]>105)&(pixels[:,:,1]>75)&(pixels[:,:,2]>pixels[:,:,0]+8))
warm=(pixels[:,:,0]>110)&(pixels[:,:,0]>pixels[:,:,1]*1.20)&(pixels[:,:,2]<pixels[:,:,1]*.95)
lamp_area=(xx>849)&(yy>140)&(yy<292)
lamp_core=lamp_area&(xx<960)&(yy<192)&(pixels[:,:,0]>160)&(pixels[:,:,1]>100)
falloff=np.clip(1-np.sqrt(((xx-916)/220)**2+((yy-176)/165)**2),0,1)
lamp_weight=warm*lamp_area*np.maximum(falloff*.65,lamp_core.astype(float))

# Connected original skyline windows, not invented lights painted onto buildings.
window_mask=((xx>522)&(xx<851)&(yy>61)&(yy<122)&(pixels[:,:,0]>95)&(pixels[:,:,1]>27)&(pixels[:,:,1]<155)&(pixels[:,:,2]<125)&(pixels[:,:,0]>pixels[:,:,1]*1.45))
seen=np.zeros((H,W),dtype=bool)
windows=[]
for y,x in zip(*np.where(window_mask)):
    if seen[y,x]:continue
    queue=[(y,x)];seen[y,x]=True;group=[]
    while queue:
        a,b=queue.pop();group.append((a,b))
        for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
            c,d=a+dy,b+dx
            if 0<=c<H and 0<=d<W and window_mask[c,d] and not seen[c,d]:seen[c,d]=True;queue.append((c,d))
    if 2<=len(group)<=40:
        windows.append((np.array([p[0] for p in group]),np.array([p[1] for p in group])))


def sparkle(draw,x,y,radius,fill):
    draw.rectangle((x-1,y-radius,x+1,y+radius),fill=fill)
    draw.rectangle((x-radius,y-1,x+radius,y+1),fill=fill)
    if radius>=5:
        for dx,dy in [(-3,-3),(3,-3),(-3,3),(3,3)]:draw.point((x+dx,y+dy),fill=fill)


def music_note(overlay,x,y,color,alpha,variant=False):
    draw=ImageDraw.Draw(overlay)
    ink=(*color,int(alpha*220))
    draw.rectangle((x+6,y-13,x+7,y+1),fill=ink)
    draw.rectangle((x,y,x+5,y+3),fill=ink)
    draw.rectangle((x+1,y-1,x+4,y+4),fill=ink)
    draw.rectangle((x+7,y-13,x+12,y-11),fill=ink)
    if variant:
        draw.rectangle((x+11,y-12,x+12,y-5),fill=ink)
        draw.rectangle((x+8,y-5,x+12,y-2),fill=ink)


def render(index):
    t=index/COUNT
    rgb=pixels.copy()
    # Strong lavender-white core, with a broader lavender shoulder.
    sweep=(t-.07)/.25
    if 0<=sweep<=1:
        distance=abs(xx-(48+sweep*350))
        wide=np.maximum(0,1-distance/28)*name
        core=np.maximum(0,1-distance/6)*name
        rgb+=wide[:,:,None]*np.array([64,73,49])+core[:,:,None]*np.array([63,67,38])
    # One gradual dim/bright cycle. The rest of the room keeps its exposure.
    lamp_level=.43+.57*(.5+.5*math.cos((t-.10)*math.tau))
    rgb*=1-lamp_weight[:,:,None]*(1-lamp_level)
    for n,(wy,wx) in enumerate(windows):
        level=.18+.94*(.5+.5*math.sin(math.tau*(t*(1+n%2)+n*.137)))
        rgb[wy,wx]*=level
    image=Image.fromarray(np.uint8(np.clip(rgb,0,255))).convert('RGBA')
    angle=1.8*math.sin(t*math.tau)
    rocking=chair.rotate(angle,Image.Resampling.NEAREST,center=(495,355),expand=False)
    image.alpha_composite(rocking)
    draw=ImageDraw.Draw(image)
    # The finishing sparkle begins after the sweep leaves the last letter.
    if .33<=t<=.415:
        progress=(t-.33)/.085
        radius=2+int(6*math.sin(progress*math.pi))
        sparkle(draw,368,139,radius,(239,226,255,255))
        for n,(dx,dy) in enumerate([(1,-1),(1,1),(-1,-1)]):
            delta=int(5+progress*11)
            if progress<.72:draw.rectangle((368+dx*delta,139+dy*delta,369+dx*delta,140+dy*delta),fill=(181,151,231,255))
    for x,y,offset in [(584,53,0),(680,37,.3),(791,43,.65)]:
        amount=(math.sin((t+offset)*math.tau)+1)/2
        color=tuple(int(a+(b-a)*amount) for a,b in zip((58,58,114),(212,199,249)))
        draw.rectangle((x,y,x+1,y+1),fill=(*color,255))
    playhead=int(707+t*118)
    draw.line((playhead,198,playhead,221),fill=(151,247,223,255),width=1)
    draw.polygon([(playhead-2,196),(playhead+2,196),(playhead,199)],fill=(184,251,232,255))
    if index%12<7:draw.rectangle((608,205,609,208),fill=(84,201,193,255))

    notes=Image.new('RGBA',(W,H))
    for n in range(3):
        phase=(t*3+n/3)%1
        x=int(899+n*15+math.sin(phase*math.tau)*5)
        y=int(323-phase*52)
        alpha=math.sin(phase*math.pi)*.86
        music_note(notes,x,y,[(173,145,229),(112,205,210),(208,174,239)][n],alpha,n==1)
    image.alpha_composite(notes)
    # Mug steam is intentionally smaller than the headphone notes.
    steam=Image.new('RGBA',(W,H));d=ImageDraw.Draw(steam)
    for offset in [0,.48]:
        phase=(t*2+offset)%1;x=523+int(math.sin(phase*math.tau)*2);y=232-int(phase*15)
        alpha=int(math.sin(phase*math.pi)*85)
        d.line([(x,y),(x,y-2),(x+1,y-3),(x+1,y-5)],fill=(179,165,198,alpha))
    image.alpha_composite(steam)
    return image.convert('RGB')


frames=[render(index) for index in range(COUNT)]
frames[0].save(OUT/'ember-studio-static-v3.png',optimize=True)
palette_source=Image.new('RGB',(W,H*5+20))
for row,index in enumerate([0,12,25,48,64]):palette_source.paste(frames[index],(0,row*H))
swatches=ImageDraw.Draw(palette_source)
for n,color in enumerate([(250,237,255),(214,190,250),(173,145,229),(112,205,210),(255,208,118),(75,42,39)]):
    swatches.rectangle((n*160,H*5,(n+1)*160-1,H*5+19),fill=color)
palette=palette_source.quantize(colors=192,method=Image.Quantize.MEDIANCUT)
indexed=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
indexed[0].save(OUT/'ember-studio-loop-v3.gif',save_all=True,append_images=indexed[1:],duration=[120,130]*(COUNT//2),loop=0,optimize=True,disposal=1)
sheet=Image.new('RGB',(W,H*4))
for row,index in enumerate([15,28,47,65]):sheet.paste(frames[index],(0,row*H))
sheet.save(OUT/'animation-contact-sheet-v3.jpg',quality=92)
report={'frames':COUNT,'duration_ms':10000,'size':[W,H],'bytes':(OUT/'ember-studio-loop-v3.gif').stat().st_size,
        'skyline_window_groups':len(windows),'chair_sway_degrees':1.8,'lamp_minimum_level':.43,
        'effects':['strong name sheen','finishing sparkle','lamp dim/bright cycle','staggered skyline window lights','rising music notes','chair sway','editor playhead','code caret','stars','steam'],
        'palette_colors':192,'publishing':'Local only; explicit approval required.'}
(OUT/'animation-build-v3.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
