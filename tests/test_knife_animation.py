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
from Characters import KnifeThrower


class KnifeTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800,600))
        self.actor=KnifeThrower(str(ROOT/'img/knife_man_sprite.png'),(250,400),4)

    def tearDown(self):
        pygame.quit()

    def test_sheet_alpha_baseline_and_distinct_frames(self):
        sheet=pygame.image.load(str(ROOT/'img/knife_animations.png'))
        self.assertEqual(sheet.get_size(),(288,160))
        unique=set()
        for y in range(2):
            for x in range(4):
                cell=sheet.subsurface((x*72,y*80,72,80))
                self.assertEqual(cell.get_bounding_rect().bottom,78)
                self.assertEqual(cell.get_at((0,0)).a,0)
                unique.add(pygame.image.tobytes(cell,'RGBA'))
        self.assertEqual(len(unique),8)

    def test_walk_and_mirror(self):
        a=self.actor
        for direction in ('left','right'):
            a.keys_pressed={'left':direction=='left','right':direction=='right'}
            a.move()
            a.update(.13)
            self.assertEqual(a.animation.state,'walk')
            self.assertEqual(a.facing,-1 if direction=='left' else 1)
        a.keys_pressed={'left':False,'right':False}
        a.move()
        a.update(.1)
        self.assertEqual(a.animation.state,'idle')

    def test_throw_one_shot_phases_freeze_and_resume(self):
        a=self.actor
        a.facing=-1
        origin=a.rect.copy()
        a.action()
        states=[a.animation.state]
        for _ in range(3):
            a.update(.12)
            states.append(a.animation.state)
            a.action()  # Repeated presses must not reset an in-progress throw.
            a.keys_pressed={'left':False,'right':True}
            a.move()
            self.assertEqual(a.rect,origin)
            self.assertEqual(a.facing,-1)
        self.assertEqual(states,['throw_0','throw_1','throw_2','throw_3'])
        right=a.animation.frame('throw_3',0,1)
        self.assertEqual(pygame.image.tobytes(a.image,'RGBA'),
                         pygame.image.tobytes(pygame.transform.flip(right,True,False),'RGBA'))
        a.update(.13)
        self.assertFalse(a.is_action)
        self.assertEqual(a.animation.state,'idle')
        a.move()
        a.update(.01)
        self.assertEqual(a.animation.state,'walk')
        a.action()
        self.assertEqual(a.animation.state,'throw_0')
        a.update(2)
        self.assertFalse(a.is_action)

    def test_switch_during_throw_in_real_loop(self):
        events=[[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_LCTRL)],
                [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE)],
                [pygame.event.Event(pygame.KEYDOWN,key=pygame.K_LCTRL)]]+[[]]*35+[[pygame.event.Event(pygame.QUIT)]]
        class Clock:
            def tick(self,fps): return 16
        with patch('pygame.event.get',side_effect=events),patch('pygame.time.Clock',Clock), \
             patch('pygame.key.get_pressed',return_value={pygame.K_LEFT:False,pygame.K_RIGHT:False}), \
             patch('pygame.key.get_focused',return_value=True):
            game=runpy.run_path(str(ROOT/'src/circus.py'))
        self.assertEqual(game['active_character'].name,'Strong man')
        self.assertFalse(game['knife_man'].is_action)
        self.assertEqual(game['knife_man'].animation.state,'idle')
        self.assertTrue(game['knife_man'].knife_released)
