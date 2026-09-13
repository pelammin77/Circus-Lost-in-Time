"""Normalize ImageGen's transparent 4x2 sheet with one shared scale. Pillow required."""
from pathlib import Path
import sys
from PIL import Image


def prepare(source, output):
    source = Image.open(source).convert('RGBA')
    frames = []
    for row in range(2):
        for col in range(4):
            cell = source.crop((round(col*source.width/4),round(row*source.height/2),
                                round((col+1)*source.width/4),round((row+1)*source.height/2)))
            # Discard only near-invisible alpha noise around generated outlines.
            alpha = cell.getchannel('A').point(lambda a: 0 if a < 32 else a)
            cell.putalpha(alpha)
            box = cell.getbbox()
            assert box and box[0]>0 and box[2]<cell.width
            frames.append(cell.crop(box))
    scale = 73/max(frame.height for frame in frames[:4])
    sheet = Image.new('RGBA',(288,160))
    for i,frame in enumerate(frames):
        frame = frame.resize((round(frame.width*scale),round(frame.height*scale)),Image.Resampling.NEAREST)
        assert frame.width <= 68 and frame.height <= 78
        # Center the body consistently; release extends to the right of the torso.
        x = (72-frame.width)//2
        if i == 6:
            x = min(x+7,71-frame.width)  # Preserve room for the extended hand.
        assert x+frame.width <= 72
        sheet.alpha_composite(frame,((i%4)*72+x,(i//4)*80+78-frame.height))
    output = Path(output)
    sheet.save(output/'knife_animations.png')
    sheet.resize((1152,640),Image.Resampling.NEAREST).save(output/'knife_animations_preview.png')
    print('RGBA sheet 288x160, 8 cells 72x80, feet baseline 78')


if __name__ == '__main__':
    prepare(sys.argv[1],sys.argv[2])
