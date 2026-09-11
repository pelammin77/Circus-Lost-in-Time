"""Normalize the generated 4x2 sheet. Requires Pillow; never overwrites the source."""
from collections import deque
from pathlib import Path
import sys
from PIL import Image


def prepare(source, output):
    source = Image.open(source).convert('RGBA')
    assert source.size == (1536, 1024)
    frames = []
    for row in range(2):
        for col in range(4):
            frame = source.crop((col*384, row*512, (col+1)*384, (row+1)*512))
            pixels = frame.load()
            # Remove only neutral bright background connected to the cell border.
            # Enclosed whites in the costume remain intact.
            queue = deque([(x, y) for x in range(384) for y in (0, 511)] +
                          [(x, y) for y in range(512) for x in (0, 383)])
            seen = set()
            while queue:
                x, y = queue.popleft()
                if not (0 <= x < 384 and 0 <= y < 512) or (x, y) in seen:
                    continue
                seen.add((x, y))
                r, g, b, a = pixels[x, y]
                if a == 0 or (min(r, g, b) >= 110 and max(r, g, b)-min(r, g, b) < 45):
                    pixels[x, y] = (0, 0, 0, 0)
                    queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
            bbox = frame.getbbox()
            assert bbox and bbox[0] > 0 and bbox[2] < 384
            frames.append(frame.crop(bbox))
    # A single scale for every pose preserves relative body proportions.
    scale = 60 / max(frame.height for frame in frames)
    sheet = Image.new('RGBA', (192, 128))
    normalized = []
    for index, frame in enumerate(frames):
        frame = frame.resize((round(frame.width*scale), round(frame.height*scale)), Image.Resampling.NEAREST)
        assert frame.width <= 44 and frame.height <= 60
        cell = Image.new('RGBA', (48, 64))
        cell.alpha_composite(frame, ((48-frame.width)//2, 62-frame.height))
        normalized.append(cell)
        sheet.alpha_composite(cell, ((index%4)*48, (index//4)*64))
    output = Path(output)
    sheet.save(output / 'acrobat_idle_walk.png')
    sheet.resize((768,512), Image.Resampling.NEAREST).save(output / 'acrobat_idle_walk_preview.png')
    preview = []
    for index in [0,1,2,3,2,1]*2 + [4,5,6,7]*4:
        canvas = Image.new('RGB', (192,256), '#79b4aa')
        sprite = normalized[index].resize((192,256), Image.Resampling.NEAREST)
        canvas.paste(sprite, (0,0), sprite)
        preview.append(canvas)
    preview[0].save(output / 'acrobat_animation_preview.gif', save_all=True,
                    append_images=preview[1:], duration=[250]*12+[120]*16, loop=0)
    print('Saved 8 RGBA frames, 48x64 cells, feet baseline 62, sheet 192x128')


if __name__ == '__main__':
    prepare(sys.argv[1], sys.argv[2])
