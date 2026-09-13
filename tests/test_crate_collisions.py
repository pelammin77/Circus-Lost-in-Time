import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
from pathlib import Path
import sys
import unittest
import runpy
from unittest.mock import patch
import pygame
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from Characters import Acrobat,KnifeThrower
from carry_objects import CircusCrate
from projectiles import FlyingKnife


class CrateCollisionTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800,600))

    def tearDown(self): pygame.quit()

    def actor(self,cls=Acrobat):
        filename='acrobat_char_sprite.png' if cls is Acrobat else 'knife_man_sprite.png'
        a=cls(str(ROOT/'img'/filename),(100,400),10)
        if cls is Acrobat: a.floor_y=a.rect.y
        box=CircusCrate((220,a.body_rect().bottom))
        a.solids=[box]
        return a,box

    def test_sides_block_both_characters_and_directions(self):
        for cls in (Acrobat,KnifeThrower):
            for direction in (-1,1):
                a,box=self.actor(cls)
                if direction<0: a.rect.x=300
                a.keys_pressed={'left':direction<0,'right':direction>0}
                for _ in range(30): a.move(); a.update(1/60)
                self.assertFalse(a.body_rect().colliderect(box.rect))
                self.assertEqual(a.body_rect().right if direction>0 else a.body_rect().left,
                                 box.rect.left if direction>0 else box.rect.right)
                self.assertFalse(a.is_moving)

    def land_on_box(self):
        a,box=self.actor()
        a.rect.x=box.rect.left-a.body_rect().width-8
        a.jump()
        for frame in range(35):
            a.keys_pressed={'left':False,'right':4<=frame<9}
            a.move()
            a.update(1/60)
        self.assertEqual(a.body_rect().bottom,box.rect.top)
        self.assertFalse(a.is_action)
        return a,box

    def test_jump_walk_on_top_and_fall_off(self):
        a,box=self.land_on_box()
        a.speed=2
        a.keys_pressed['right']=True
        a.move();a.update(1/60)
        self.assertEqual(a.body_rect().bottom,box.rect.top)
        for _ in range(70): a.move();a.update(1/60)
        self.assertEqual(a.rect.y,a.floor_y)
        self.assertFalse(a.is_action)

    def test_jump_again_from_box(self):
        a,box=self.land_on_box()
        y=a.rect.y
        a.jump();a.update(1/60)
        self.assertLess(a.rect.y,y)
        for _ in range(30): a.update(1/60)
        self.assertEqual(a.body_rect().bottom,box.rect.top)

    def test_removed_support_causes_fall(self):
        a,box=self.land_on_box()
        box.rect.x+=200
        for _ in range(40): a.update(1/60)
        self.assertEqual(a.rect.y,a.floor_y)

    def test_knife_stops_without_tunnelling_and_expires(self):
        box=CircusCrate((400,300))
        for direction in (-1,1):
            k=FlyingKnife((100 if direction>0 else 700,280),direction,obstacles=[box])
            group=pygame.sprite.Group(k)
            k.update(1)
            self.assertIs(k.stuck_to,box)
            x=k.position.x
            k.update(.2)
            self.assertEqual(k.position.x,x)
            k.update(1)
            self.assertEqual(len(group),0)

    def test_knife_above_box_passes(self):
        box=CircusCrate((400,300))
        k=FlyingKnife((100,200),1,obstacles=[box])
        k.update(1)
        self.assertIsNone(k.stuck_to)

    def test_actual_game_loop_lands_on_demo_crate(self):
        step=[-1]
        def events():
            step[0]+=1
            if step[0]==30: return [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE)]
            if step[0]==65: return [pygame.event.Event(pygame.QUIT)]
            return []
        class Clock:
            def tick(self,fps): return 16
        with patch('pygame.event.get',events),patch('pygame.time.Clock',Clock), \
             patch('pygame.key.get_pressed',side_effect=lambda:{pygame.K_LEFT:False,pygame.K_RIGHT:step[0]<37}), \
             patch('pygame.key.get_focused',return_value=True):
            game=runpy.run_path(str(ROOT/'src/circus.py'))
        self.assertEqual(game['acrobat'].body_rect().bottom,next(iter(game['crates'])).rect.top)
        self.assertFalse(game['acrobat'].is_action)
