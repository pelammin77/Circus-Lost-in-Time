"""Actual character and projectile code rendered into a slowed GIF."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
from pathlib import Path
import sys
import pygame
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from Characters import KnifeThrower
pygame.init()
screen=pygame.display.set_mode((520,180))
actor=KnifeThrower(str(ROOT/'img/knife_man_sprite.png'),(55,80),4)
actor.win_width=520
frames=[]
for n in range(170):
    if n==12: actor.action()
    if n==92:
        actor.rect.x=390
        actor.facing=-1
        actor.action()
    actor.update(1/60)
    screen.fill((126,173,169))
    pygame.draw.line(screen,(60,92,80),(0,actor.rect.bottom-2),(520,actor.rect.bottom-2),2)
    screen.blit(actor.image,actor.rect)
    actor.projectiles.draw(screen)
    im=Image.frombytes('RGB',screen.get_size(),pygame.image.tobytes(screen,'RGB'))
    frames.append(im.resize((1040,360),Image.Resampling.NEAREST))
frames[0].save(ROOT/'img/flying_knife_preview.gif',save_all=True,append_images=frames[1:],duration=30,loop=0)
frames[45].save(ROOT/'img/flying_knife_preview.png')
pygame.quit()
