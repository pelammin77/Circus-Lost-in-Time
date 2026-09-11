"""Normalize generated jump poses without changing existing idle/walk pixels."""
from collections import deque
from pathlib import Path
import sys
from PIL import Image


def prepare(source, output):
    source = Image.open(source).convert('RGBA')
    width, height = source.width//2, source.height//2
    frames = []
    centers = []
    for row in range(2):
        for col in range(2):
            frame = source.crop((col*width,row*height,(col+1)*width,(row+1)*height))
            pixels = frame.load()
            queue = deque([(x,y) for x in range(width) for y in (0,height-1)] +
                          [(x,y) for y in range(height) for x in (0,width-1)])
            seen = set()
            while queue:
                x,y = queue.popleft()
                if not (0 <= x < width and 0 <= y < height) or (x,y) in seen:
                    continue
                seen.add((x,y))
                r,g,b,a = pixels[x,y]
                if a == 0 or (min(r,g,b) >= 110 and max(r,g,b)-min(r,g,b) < 45):
                    pixels[x,y] = (0,0,0,0)
                    queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
            bbox = frame.getbbox()
            assert bbox and bbox[0] > 0 and bbox[2] < width
            head = frame.crop((0,bbox[1],width,bbox[1]+220)).getbbox()
            centers.append((head[0]+head[2])/2 - bbox[0])
            frames.append(frame.crop(bbox))
    scale = 60/max(frame.height for frame in frames)
    output = Path(output)
    jumps = Image.new('RGBA',(192,64))
    for index,frame in enumerate(frames):
        frame = frame.resize((round(frame.width*scale),round(frame.height*scale)), Image.Resampling.NEAREST)
        x = round(25-centers[index]*scale)
        # Airborne poses share the head anchor; tucked feet rise inside the cell.
        # The recovery pose is grounded at the existing feet baseline.
        y = 62-frame.height if index == 3 else 2
        assert x >= 0 and x+frame.width <= 48 and y+frame.height <= 62
        jumps.alpha_composite(frame,(index*48+x,y))
    jumps.save(output/'acrobat_jump.png')
    old = Image.open(output/'acrobat_idle_walk.png').convert('RGBA')
    combined = Image.new('RGBA',(192,192))
    combined.alpha_composite(old)
    combined.alpha_composite(jumps,(0,128))
    combined.save(output/'acrobat_animations.png')
    combined.resize((768,768),Image.Resampling.NEAREST).save(output/'acrobat_animations_preview.png')
    print('Prepared 4 jump poses and 12-frame combined atlas; existing pixels preserved')


if __name__ == '__main__':
    prepare(sys.argv[1],sys.argv[2])
