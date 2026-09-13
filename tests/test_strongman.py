import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import runpy
import pygame
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from Characters import Strongman
from carry_objects import CircusCrate


class StrongmanTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800,600))
        self.actor=Strongman(str(ROOT/'img/strong_man_char_sprite.png'),(350,400),2)
        self.crate=CircusCrate(self.actor.ground_target().midbottom)
        self.actor.crates=[self.crate]

    def tearDown(self): pygame.quit()

    def test_art_contract(self):
        sheet=pygame.image.load(str(ROOT/'img/strongman_animations.png'))
        lower=pygame.image.load(str(ROOT/'img/strongman_lower.png'))
        self.assertEqual(sheet.get_size(),(384,320))
        unique=set()
        for row in range(4):
            for col in range(4):
                cell=sheet.subsurface((col*96,row*80,96,80))
                self.assertEqual(cell.get_bounding_rect().bottom,78)
                self.assertEqual(cell.get_at((0,0)).a,0)
                unique.add(pygame.image.tobytes(cell,'RGBA'))
        self.assertEqual(len(unique),16)
        for col in range(4):
            self.assertEqual(pygame.image.tobytes(lower.subsurface((col*96,0,96,80)),'RGBA'),
                             pygame.image.tobytes(sheet.subsurface(((3-col)*96,80,96,80)),'RGBA'))

    def test_lift_hold_carry_lower_cycle(self):
        a=self.actor
        ground=self.crate.rect.bottom
        a.action()
        states=[a.animation.state]
        for _ in range(3):
            a.update(.21)
            states.append(a.animation.state)
            a.action()  # Does not restart the action.
        self.assertEqual(states,['lift_0','lift_1','lift_2','lift_3'])
        a.update(.2)
        self.assertEqual(a.animation.state,'hold')
        self.assertIs(self.crate.holder,a)
        self.assertLess(self.crate.rect.bottom,ground)
        a.keys_pressed['right']=True
        before=a.rect.x
        a.move()
        a.update(.01)
        self.assertEqual(a.rect.x-before,1)
        self.assertEqual(a.animation.state,'carry')
        a.keys_pressed['right']=False
        a.move()
        a.action()
        states=[a.animation.state]
        for _ in range(3):
            a.update(.21)
            states.append(a.animation.state)
        self.assertEqual(states,['lower_0','lower_1','lower_2','lower_3'])
        a.update(.2)
        self.assertIsNone(a.carried)
        self.assertIsNone(self.crate.holder)
        self.assertEqual(self.crate.rect.bottom,ground)
        self.assertEqual(a.animation.state,'idle')
        a.action()
        self.assertTrue(a.is_action)

    def test_blocked_drop_and_mid_action_obstruction(self):
        a=self.actor
        a.action()
        a.update(1)
        obstacle=CircusCrate(a.ground_target().midbottom)
        a.crates.append(obstacle)
        a.action()
        self.assertFalse(a.is_action)
        self.assertIsNotNone(a.carried)
        a.crates.remove(obstacle)
        a.action()
        a.crates.append(obstacle)
        a.update(1)
        self.assertIs(self.crate.holder,a)
        self.assertEqual(a.motion,'lower')
        a.crates.remove(obstacle)
        a.update(1)
        self.assertIsNone(a.carried)

    def test_push_walk_facing_and_edges(self):
        a=self.actor
        self.crate.rect.left=a.rect.left+70
        before=self.crate.rect.x
        a.keys_pressed['right']=True
        a.move()
        a.update(.1)
        self.assertEqual(a.animation.state,'push')
        self.assertGreater(self.crate.rect.x,before)
        a.keys_pressed={'left':True,'right':False}
        before=self.crate.rect.x
        a.move()
        self.assertEqual(self.crate.rect.x,before)  # Moving away must not pull the crate.
        a.crates=[]
        a.keys_pressed={'left':True,'right':False}
        a.move()
        a.update(.1)
        self.assertEqual(a.facing,-1)
        self.assertEqual(a.animation.state,'walk')
        frame=a.animation.frame('walk',0,1)
        self.assertEqual(pygame.image.tobytes(a.image,'RGBA'),
                         pygame.image.tobytes(pygame.transform.flip(frame,True,False),'RGBA'))
        a.rect.x=0
        a.move()
        self.assertEqual(a.rect.x,0)

    def test_no_crate_no_lift(self):
        self.actor.crates=[]
        self.actor.action()
        self.assertFalse(self.actor.is_action)
        self.assertIsNone(self.actor.carried)

    def test_lift_directly_from_push_contact_both_directions(self):
        for direction in (-1,1):
            for gap in (0,5):
                with self.subTest(direction=direction,gap=gap):
                    a=Strongman(str(ROOT/'img/strong_man_char_sprite.png'),(350,400),2)
                    crate=CircusCrate(a.ground_target().midbottom)
                    if direction>0:
                        crate.rect.left=a.rect.left+70+gap
                    else:
                        crate.rect.right=a.rect.left+26-gap
                    a.crates=[crate]
                    a.keys_pressed={'left':direction<0,'right':direction>0}
                    for _ in range(10):
                        a.move()
                        a.update(1/60)
                    self.assertEqual(a.animation.state,'push')
                    a.action()  # Space while still holding the direction key.
                    self.assertEqual(a.motion,'lift')
                    position=a.rect.copy()
                    a.move()
                    self.assertEqual(a.rect,position)
                    a.update(1)
                    self.assertIs(a.carried,crate)
                    self.assertEqual(a.animation.state,'hold')

    def test_lift_after_releasing_push_key(self):
        a=self.actor
        self.crate.rect.left=a.rect.left+70
        a.keys_pressed['right']=True
        a.move()
        a.keys_pressed['right']=False
        a.move()
        a.update(.01)
        self.assertFalse(a.is_pushing)
        a.action()
        self.assertEqual(a.motion,'lift')

    def test_distant_crate_cannot_be_lifted(self):
        self.crate.rect.x+=200
        self.actor.action()
        self.assertIsNone(self.actor.carried)

    def test_switch_during_lift_keeps_holding(self):
        ctrl=lambda:pygame.event.Event(pygame.KEYDOWN,key=pygame.K_LCTRL)
        events=[[ctrl(),ctrl()],[pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE)],[ctrl()]]+[[]]*60+[[pygame.event.Event(pygame.QUIT)]]
        class Clock:
            def tick(self,fps): return 16
        def feed():
            game=sys._getframe(1).f_globals
            if len(events)==64:
                game['strong_man'].rect.x=350
                next(iter(game['crates'])).rect=game['strong_man'].ground_target()
            return events.pop(0)
        with patch('pygame.event.get',feed),patch('pygame.time.Clock',Clock), \
             patch('pygame.key.get_pressed',return_value={pygame.K_LEFT:False,pygame.K_RIGHT:False}), \
             patch('pygame.key.get_focused',return_value=True):
            game=runpy.run_path(str(ROOT/'src/circus.py'))
        self.assertEqual(game['active_character'].name,'Acrobat')
        self.assertEqual(game['strong_man'].animation.state,'hold')
        self.assertIsNotNone(game['strong_man'].carried)
