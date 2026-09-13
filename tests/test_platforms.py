import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
from pathlib import Path
import sys
import runpy
import unittest
from unittest.mock import patch
import pygame
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from Characters import Acrobat, Strongman
from platforms import Platform,GROUND_TOP
from carry_objects import CircusCrate
from projectiles import FlyingKnife

class PlatformTests(unittest.TestCase):
    def setUp(self):
        pygame.init();pygame.display.set_mode((800,600))
        with patch('pygame.event.get',return_value=[pygame.event.Event(pygame.QUIT)]),patch('pygame.quit'):
            self.game=runpy.run_path(str(ROOT/'src/circus.py'))
        self.actor=self.game['acrobat']
        self.platform=self.game['upper_platform']
        self.box=next(iter(self.game['crates']))
    def tearDown(self): pygame.quit()
    def step(self,n=1,right=False,left=False):
        a=self.actor
        a.keys_pressed={'right':right,'left':left}
        for _ in range(n): a.move();a.update(1/60)
        self.assertFalse(a.body_rect().colliderect(self.platform.rect))
        self.assertFalse(a.body_rect().colliderect(self.box.rect))
    def test_direct_jump_cannot_reach_and_ceiling_is_solid(self):
        a=self.actor
        a.rect.x=550
        a.jump()
        for _ in range(30): self.step()
        self.assertEqual(a.body_rect().bottom,GROUND_TOP)
        a.rect.x=400
        a.jump()
        heights=[]
        for _ in range(30):
            self.step();heights.append(a.body_rect().bottom)
        self.assertGreater(min(heights),self.platform.rect.top)
    def test_push_box_jump_to_box_then_platform_and_walk_off(self):
        strong=self.game['strong_man']
        strong.keys_pressed['right']=True
        for _ in range(500):
            strong.move();strong.update(1/60)
            if self.box.rect.left>=440:break
        self.assertEqual(self.box.rect.left,440)
        a=self.actor
        self.step(30,right=True)
        a.jump()
        for frame in range(30):self.step(right=4<=frame<8)
        self.assertEqual(a.body_rect().bottom,self.box.rect.top)
        a.jump()
        for frame in range(30):self.step(right=5<=frame<12)
        self.assertEqual(a.body_rect().bottom,self.platform.rect.top)
        self.step(25,right=True)
        self.step(30)
        self.assertEqual(a.body_rect().bottom,GROUND_TOP)
    def test_characters_are_not_obstacles(self):
        actors=self.game['characters']
        for a in actors:
            self.assertFalse(any(b in a.solids for b in actors))
        a=self.actor
        a.rect.x=300
        other=self.game['knife_man'];other.rect.x=330
        self.step(12,right=True)
        self.assertGreater(a.body_rect().left,other.body_rect().right)
    def test_sides_and_carried_box_blocked_by_platform(self):
        a=self.actor
        a.rect.bottom=self.platform.rect.bottom+20
        a.rect.right=self.platform.rect.left
        self.step(10,right=True)
        self.assertLessEqual(a.body_rect().right,self.platform.rect.left)
        strong=self.game['strong_man']
        strong.rect.x=350
        self.box.rect=strong.ground_target()
        strong.action();strong.update(1)
        self.assertIs(strong.carried,self.box)
        strong.keys_pressed['right']=True
        for _ in range(200):
            strong.move();strong.update(1/60)
            self.assertFalse(self.box.rect.colliderect(self.platform.rect))
            self.assertFalse(strong.body_rect().colliderect(self.platform.rect))
        self.assertFalse(strong.is_moving)
    def test_lift_and_push_paths_cannot_cross_solid(self):
        strong=self.game['strong_man']
        strong.rect.x=450
        self.box.rect=strong.ground_target()
        strong.action()
        self.assertIsNone(strong.carried)
        wall=Platform((self.box.rect.right,480,20,60))
        strong.blockers.append(wall)
        strong.solids.append(wall)
        before=self.box.rect.copy()
        strong.keys_pressed['right']=True
        for _ in range(10):strong.move()
        self.assertEqual(self.box.rect,before)
    def test_knife_stops_at_platform(self):
        knife=FlyingKnife((400,self.platform.rect.centery),1,obstacles=[self.platform])
        knife.update(1)
        self.assertIs(knife.stuck_to,self.platform)

    def test_ground_characters_can_walk_under_platform_both_directions(self):
        for actor in (self.game['knife_man'],self.game['strong_man']):
            for direction in (-1,1):
                with self.subTest(actor=actor.name,direction=direction):
                    actor.rect.x=720 if direction<0 else 400
                    actor.keys_pressed={'left':direction<0,'right':direction>0}
                    self.assertGreaterEqual(actor.body_rect().top,self.platform.rect.bottom)
                    for _ in range(170):
                        actor.move();actor.update(1/60)
                        self.assertFalse(actor.body_rect().colliderect(self.platform.rect))
                    if direction<0:
                        self.assertLess(actor.body_rect().right,self.platform.rect.left)
                    else:
                        self.assertGreater(actor.body_rect().left,self.platform.rect.right)
