"""Render the actual Acrobat.update jump states into a GIF using SDL dummy."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
from pathlib import Path
import sys
from PIL import Image, ImageDraw
import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from Characters import Acrobat


def render():
    pygame.init()
    pygame.display.set_mode((800,600))
    actor = Acrobat(str(ROOT/'img/acrobat_char_sprite.png'),(100,400),10)
    actor.rect.y = 530
    frames = []
    labels = {'idle':'SEISONTA', 'rise':'NOUSU', 'apex':'LAKIPISTE', 'fall':'LASKU', 'land':'LASKEUTUMINEN'}
    for step in range(74):
        if step in (18,48):
            actor.facing = 1 if step == 18 else -1
            actor.jump()
        actor.update(1/60)
        canvas = Image.new('RGB',(288,512),'#79b4aa')
        draw = ImageDraw.Draw(canvas)
        draw.line((0,460,288,460),fill='#345449',width=3)
        draw.text((16,14),labels[actor.animation.state],fill='#142c28')
        sprite = Image.frombytes('RGBA',(48,64),pygame.image.tobytes(actor.image,'RGBA'))
        sprite = sprite.resize((192,256),Image.Resampling.NEAREST)
        y = 460-248+round((actor.rect.y-530)*3)
        canvas.paste(sprite,(48,y),sprite)
        frames.append(canvas)
    frames[0].save(ROOT/'img/acrobat_jump_preview.gif',save_all=True,append_images=frames[1:],duration=40,loop=0)
    # Slowed playback makes each actual game state easy to inspect.
    montage = Image.new('RGB',(288*5,512))
    for i,step in enumerate((10,19,27,33,39)):
        montage.paste(frames[step],(i*288,0))
    montage.save(ROOT/'img/acrobat_jump_contact_sheet.png')
    pygame.quit()


if __name__ == '__main__':
    render()
