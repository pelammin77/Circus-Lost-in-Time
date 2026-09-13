"""Preview actual Strongman and crate state transitions (Pygame + Pillow)."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
from pathlib import Path
import sys
import pygame
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from Characters import Strongman
from carry_objects import CircusCrate
pygame.init()
pygame.display.set_mode((800,600))
actor=Strongman(str(ROOT/'img/strong_man_char_sprite.png'),(100,400),2)
crate=CircusCrate(actor.ground_target().midbottom)
frames=[]
labels={'idle':'SEISONTA','walk':'KÄVELY','hold':'KANNATTELU','carry':'KANTOKÄVELY','push':'TYÖNTÖ'}
for step in range(260):
    actor.keys_pressed={'left':False,'right':step<20 or 100<=step<135 or 210<=step<245}
    if step==30:
        crate.rect=actor.ground_target()
        actor.crates=[crate]
        actor.action()
    if step==145: actor.action()
    if step==210: actor.rect.x=crate.rect.left-70
    actor.move()
    actor.update(1/60)
    scene=Image.new('RGB',(384,352),'#82ada5')
    draw=ImageDraw.Draw(scene)
    state=actor.animation.state
    label='NOSTO' if state.startswith('lift') else 'LASKEMINEN' if state.startswith('lower') else labels[state]
    draw.text((16,12),label,fill='#203d35')
    draw.line((0,320,384,320),fill='#446958',width=2)
    sprite=Image.frombytes('RGBA',(96,80),pygame.image.tobytes(actor.image,'RGBA')).resize((288,240),Image.Resampling.NEAREST)
    scene.paste(sprite,(48,86),sprite)
    if step>=30:
        box=Image.frombytes('RGBA',(40,40),pygame.image.tobytes(crate.image,'RGBA')).resize((120,120),Image.Resampling.NEAREST)
        x=48+(crate.rect.x-actor.rect.x)*3
        y=86+(crate.rect.y-actor.rect.y)*3
        scene.paste(box,(x,y),box)
    frames.append(scene)
frames[0].save(ROOT/'img/strongman_actions_preview.gif',save_all=True,append_images=frames[1:],duration=25,loop=0)
montage=Image.new('RGB',(384*4,352*2))
for i,n in enumerate((12,33,57,81,111,153,181,221)):
    montage.paste(frames[n],((i%4)*384,(i//4)*352))
montage.save(ROOT/'img/strongman_actions_contact_sheet.png')
pygame.quit()
