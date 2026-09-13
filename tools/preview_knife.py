"""Render walk/throw playback from the actual character code. Requires Pillow/Pygame."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
from pathlib import Path
import sys
import pygame
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from Characters import KnifeThrower

pygame.init()
pygame.display.set_mode((800,600))
actor=KnifeThrower(str(ROOT/'img/knife_man_sprite.png'),(250,400),4)
frames=[]
for step in range(116):
    actor.keys_pressed={'left':58<=step<76,'right':step<18}
    if step in (22,80): actor.action()
    actor.move()
    actor.update(1/60)
    canvas=Image.new('RGB',(288,352),'#92b7b0')
    draw=ImageDraw.Draw(canvas)
    draw.text((12,10),actor.animation.state.upper(),fill='#182b26')
    draw.line((0,336,288,336),fill='#456457',width=2)
    sprite=Image.frombytes('RGBA',(72,80),pygame.image.tobytes(actor.image,'RGBA'))
    sprite=sprite.resize((288,320),Image.Resampling.NEAREST)
    canvas.paste(sprite,(0,24),sprite)
    frames.append(canvas)
frames[0].save(ROOT/'img/knife_animation_preview.gif',save_all=True,append_images=frames[1:],duration=35,loop=0)
montage=Image.new('RGB',(288*5,352))
for i,n in enumerate((10,22,30,38,46)): montage.paste(frames[n],(i*288,0))
montage.save(ROOT/'img/knife_animation_contact_sheet.png')
pygame.quit()
