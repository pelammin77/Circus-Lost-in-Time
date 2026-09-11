"""Functional checks against real game/editor loops with simulated input."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import inspect
from pathlib import Path
import runpy
import sys
import unittest
from unittest.mock import patch
import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from Characters import Acrobat, KnifeThrower, Strongman


class FastClock:
    def tick(self, fps):
        return 16


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800,600))

    def tearDown(self):
        pygame.quit()

    def actors(self):
        return [cls(str(ROOT/'img'/file),(100,400),speed) for cls,file,speed in
                [(Acrobat,'acrobat_char_sprite.png',10),
                 (KnifeThrower,'knife_man_sprite.png',4),
                 (Strongman,'strong_man_char_sprite.png',2)]]

    def test_first_and_repeated_jump_returns_to_launch_height(self):
        actor = self.actors()[0]
        for _ in range(3):
            original = actor.rect.midbottom
            actor.jump()
            for frame in range(100):
                actor.update(1/60)
                if not actor.is_action:
                    break
            self.assertFalse(actor.is_action)
            self.assertEqual(actor.rect.midbottom, original)

    def test_both_arrows_cancel_at_both_edges(self):
        for actor in self.actors():
            for x in (0,400,800-actor.rect.width):
                actor.rect.x = x
                actor.keys_pressed = {'left':True,'right':True}
                actor.move()
                self.assertEqual(actor.rect.x,x)
                self.assertFalse(actor.is_moving)

    def test_edges_and_both_directions(self):
        for actor in self.actors():
            for direction,expected in [('left',0),('right',800-actor.rect.width)]:
                actor.keys_pressed = {'left':direction=='left','right':direction=='right'}
                for _ in range(500):
                    actor.move()
                    actor.update(1/60)
                    self.assertGreaterEqual(actor.rect.left,0)
                    self.assertLessEqual(actor.rect.right,800)
                self.assertEqual(actor.rect.x,expected)
                self.assertFalse(actor.is_moving)
                if actor.animation:
                    self.assertEqual(actor.animation.state,'idle')

    def run_game(self, cwd, count=60):
        frames = []
        step = [-1]
        original_get = pygame.event.get
        original_flip = pygame.display.flip
        def events():
            step[0] += 1
            n = step[0]
            schedule = {2:pygame.K_SPACE,4:pygame.K_LCTRL,8:pygame.K_RCTRL,
                        12:pygame.K_LCTRL,32:pygame.K_SPACE}
            if n in schedule:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN,key=schedule[n]))
            if n == count-1:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return original_get()
        def keys():
            return {pygame.K_LEFT:step[0]>=25 and step[0]<45,
                    pygame.K_RIGHT:step[0]<16}
        def flip():
            game = inspect.currentframe().f_back.f_globals
            frames.append([(a.rect.copy(),a.is_action,a.facing,
                            a.animation.state if a.animation else None,dict(a.keys_pressed))
                           for a in game['characters']])
            original_flip()
        old = Path.cwd()
        try:
            os.chdir(cwd)
            with patch('pygame.event.get',events), patch('pygame.key.get_pressed',keys), \
                 patch('pygame.key.get_focused',side_effect=lambda:step[0]!=14), \
                 patch('pygame.time.Clock',FastClock),patch('pygame.display.flip',flip):
                game = runpy.run_path(str(ROOT/'src/circus.py'))
            self.assertFalse(pygame.get_init())
            return frames,game
        finally:
            os.chdir(old)

    def test_game_loop_switch_held_arrows_airborne_focus_and_close(self):
        frames,game = self.run_game(ROOT)
        self.assertEqual(len(frames),60)
        self.assertEqual(frames[4][0][0].x,frames[3][0][0].x)
        self.assertLess(frames[4][0][0].y,frames[3][0][0].y)
        self.assertGreater(frames[4][1][0].x,frames[3][1][0].x)
        self.assertGreater(frames[8][2][0].x,frames[7][2][0].x)
        self.assertGreater(frames[12][0][0].x,frames[11][0][0].x)
        for index in range(3):
            self.assertEqual(frames[14][index][0].x,frames[13][index][0].x)
            self.assertFalse(frames[14][index][4]['right'])
        self.assertEqual(frames[26][0][2],-1)
        self.assertFalse(frames[-1][0][1])
        self.assertEqual(frames[-1][0][3],'idle')
        states = {frame[0][3] for frame in frames}
        self.assertTrue({'idle','walk','rise','apex','fall','land'} <= states)
        self.assertEqual(game['active_character'].name,'Acrobat')

    def test_game_launch_from_src_and_unrelated_directory(self):
        for cwd in (ROOT/'src', ROOT.parent):
            frames,_ = self.run_game(cwd,2)
            self.assertEqual(len(frames),2)

    def test_editor_paints_corners_center_and_closes(self):
        ticks = [0]
        original_get = pygame.event.get
        original_flip = pygame.display.flip
        captured = []
        def events():
            if ticks[0] == 0:
                for pos in ((0,0),(799,599),(400,300)):
                    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN,pos=pos,button=1))
            else:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            ticks[0] += 1
            return original_get()
        def flip():
            captured.append(pygame.display.get_surface().copy())
            original_flip()
        with patch('pygame.event.get',events),patch('pygame.display.flip',flip),patch('pygame.time.Clock',FastClock):
            game = runpy.run_path(str(ROOT/'src/editor.py'))
        self.assertFalse(pygame.get_init())
        self.assertEqual(sum(map(sum,game['grid'])),3)
        for pos in ((0,0),(799,599),(400,300)):
            self.assertEqual(captured[0].get_at(pos)[:3],(255,255,255))
        self.assertEqual(captured[0].get_at((100,100))[:3],(0,0,0))

    def test_all_png_assets_decode(self):
        paths = list((ROOT/'img').glob('*.png'))
        self.assertGreater(len(paths),10)
        for path in paths:
            image = pygame.image.load(str(path))
            self.assertGreater(image.get_width(),0)


if __name__ == '__main__':
    unittest.main()
