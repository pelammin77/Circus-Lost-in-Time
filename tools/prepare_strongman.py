"""Technical normalization of generated strongman art; requires Pillow."""
from collections import deque
from pathlib import Path
import sys
from PIL import Image


def prepare(folder):
    folder=Path(folder)
    source=Image.open(folder/'strongman_source.png').convert('RGBA')
    assert source.size == (1245,1263)
    xs=(0,330,625,930,1245)
    ys=(0,316,630,945,1263)
    frames=[]
    heads=[]
    for row in range(4):
        for col in range(4):
            cell=source.crop((xs[col],ys[row],xs[col+1],ys[row+1]))
            pix=cell.load()
            queue=deque([(x,y) for x in range(cell.width) for y in (0,cell.height-1)]+
                        [(x,y) for y in range(cell.height) for x in (0,cell.width-1)])
            seen=set()
            while queue:
                x,y=queue.popleft()
                if not (0<=x<cell.width and 0<=y<cell.height) or (x,y) in seen: continue
                seen.add((x,y))
                r,g,b,a=pix[x,y]
                if a==0 or (min(r,g,b)>210 and max(r,g,b)-min(r,g,b)<25):
                    pix[x,y]=(0,0,0,0)
                    queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
            bbox=cell.getbbox()
            assert bbox
            frame=cell.crop(bbox)
            head=frame.crop((0,0,frame.width,min(35,frame.height))).getbbox()
            heads.append((head[0]+head[2])/2)
            frames.append(frame)
    scale=75/max(f.height for f in frames[:4])
    sheet=Image.new('RGBA',(384,320))
    for i,frame in enumerate(frames):
        frame=frame.resize((round(frame.width*scale),round(frame.height*scale)),Image.Resampling.NEAREST)
        x=round(45-heads[i]*scale)
        assert x>=0 and x+frame.width<=96 and frame.height<=78,(i,x,frame.size)
        sheet.alpha_composite(frame,((i%4)*96+x,(i//4)*80+78-frame.height))
    sheet.save(folder/'strongman_animations.png')
    sheet.resize((1152,960),Image.Resampling.NEAREST).save(folder/'strongman_animations_preview.png')
    crate=Image.open(folder/'crate_source.png').convert('RGBA')
    crate.putalpha(crate.getchannel('A').point(lambda a:255 if a>=128 else 0))
    crate=crate.crop(crate.getbbox()).resize((40,40),Image.Resampling.NEAREST)
    crate.save(folder/'circus_crate.png')
    # Lowering is the exact reverse of the lift: export an explicit usable row.
    lower=Image.new('RGBA',(384,80))
    for i in range(4): lower.alpha_composite(sheet.crop(((3-i)*96,80,(4-i)*96,160)),(i*96,0))
    lower.save(folder/'strongman_lower.png')
    print('16 frames, 96x80 RGBA, baseline 78; separate lowering strip and 40x40 crate')


if __name__=='__main__': prepare(sys.argv[1])
