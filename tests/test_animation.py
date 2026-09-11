"""Headless regression checks: python -B -m unittest discover -s tests."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import runpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import pygame
from Characters import Acrobat, KnifeThrower, Strongman


class AnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((800, 600))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def acrobat(self):
        return Acrobat(str(ROOT/'img/acrobat_char_sprite.png'), (100, 400), 10)

    def test_sheet_contract(self):
        sheet = pygame.image.load(str(ROOT/'img/acrobat_idle_walk.png'))
        self.assertEqual(sheet.get_size(), (192,128))
        hashes = set()
        for row in range(2):
            for col in range(4):
                cell = sheet.subsurface((col*48,row*64,48,64))
                self.assertEqual(cell.get_bounding_rect().bottom, 62)
                self.assertEqual(cell.get_at((0,0)).a, 0)
                self.assertEqual(cell.get_bounding_rect().clip(cell.get_rect()),cell.get_bounding_rect())
                hashes.add(pygame.image.tobytes(cell, 'RGBA'))
        self.assertEqual(len(hashes), 8)

    def test_idle_walk_stop_and_facing(self):
        actor = self.acrobat()
        feet = actor.rect.midbottom
        first = pygame.image.tobytes(actor.image, 'RGBA')
        actor.update(.3)
        self.assertNotEqual(first, pygame.image.tobytes(actor.image, 'RGBA'))
        self.assertEqual(actor.rect.midbottom, feet)
        actor.keys_pressed['right'] = True
        actor.move()
        actor.update(.1)
        self.assertEqual(actor.animation.state, 'walk')
        actor.keys_pressed = {'left': True, 'right': False}
        actor.move()
        actor.update(0)
        self.assertEqual(actor.facing, -1)
        right = actor.animation.frame('walk', 0, 1)
        self.assertEqual(pygame.image.tobytes(actor.image,'RGBA'),
                         pygame.image.tobytes(pygame.transform.flip(right,True,False),'RGBA'))
        actor.keys_pressed['left'] = False
        actor.move()
        actor.update(.1)
        self.assertEqual(actor.animation.state, 'idle')

    def test_animation_timing_and_jump(self):
        a, b = self.acrobat(), self.acrobat()
        for _ in range(60): a.update(1/60)
        for _ in range(20): b.update(1/20)
        self.assertEqual(pygame.image.tobytes(a.image,'RGBA'), pygame.image.tobytes(b.image,'RGBA'))
        a.jump()
        y = a.rect.y
        a.update(1/60)
        self.assertLess(a.rect.y, y)
        self.assertEqual(a.animation.state, 'rise')

    def test_jump_atlas_preserves_existing_frames(self):
        sheet = pygame.image.load(str(ROOT/'img/acrobat_animations.png'))
        old = pygame.image.load(str(ROOT/'img/acrobat_idle_walk.png'))
        self.assertEqual(sheet.get_size(), (192,192))
        self.assertEqual(pygame.image.tobytes(sheet.subsurface((0,0,192,128)), 'RGBA'),
                         pygame.image.tobytes(old, 'RGBA'))
        poses = set()
        for col in range(4):
            cell = sheet.subsurface((col*48,128,48,64))
            bounds = cell.get_bounding_rect()
            self.assertGreater(bounds.width, 0)
            self.assertGreater(bounds.left, 0)
            self.assertLess(bounds.right, 48)
            self.assertGreaterEqual(bounds.top, 2)
            self.assertLessEqual(bounds.bottom, 62)
            self.assertEqual(cell.get_at((0,0)).a, 0)
            poses.add(pygame.image.tobytes(cell, 'RGBA'))
        self.assertEqual(len(poses), 4)

    def test_jump_phases_landing_and_resume(self):
        for walking in (False, True):
            actor = self.acrobat()
            actor.rect.y = 530
            actor.is_moving = walking
            actor.jump()
            phases = []
            while actor.is_action:
                actor.update(1/60)
                state = actor.animation.state
                if not phases or phases[-1] != state:
                    phases.append(state)
                self.assertLess(len(phases), 10)
                if actor.is_action:
                    expected = ('apex' if abs(actor.vertical_velocity) <= 2 else
                                'rise' if actor.vertical_velocity < 0 else 'fall')
                    self.assertEqual(state, expected)
            self.assertEqual(phases, ['rise','apex','fall','land'])
            self.assertEqual(actor.rect.y, 530)
            actor.update(.1)
            self.assertEqual(actor.animation.state, 'walk' if walking else 'idle')
            actor.jump()
            actor.update(1/60)
            self.assertEqual(actor.animation.state, 'rise')

    def test_airborne_facing_and_no_double_jump(self):
        actor = self.acrobat()
        actor.jump()
        actor.update(1/60)
        velocity = actor.vertical_velocity
        actor.jump()
        self.assertEqual(actor.vertical_velocity, velocity)
        actor.facing = -1
        actor.update(0)
        frame = actor.animation.frame(actor.animation_state(),0,1)
        self.assertEqual(pygame.image.tobytes(actor.image,'RGBA'),
                         pygame.image.tobytes(pygame.transform.flip(frame,True,False),'RGBA'))

    def test_other_characters(self):
        for cls, name in [(KnifeThrower,'knife_man_sprite.png'),(Strongman,'strong_man_char_sprite.png')]:
            actor = cls(str(ROOT/'img'/name), (250,400), 4)
            actor.keys_pressed['right'] = True
            actor.move()
            actor.update(.1)
            actor.action()
            self.assertEqual(actor.rect.x, 254)

    def test_game_loop_and_character_switch(self):
        events = [[], [], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LCTRL)],
                  [], [pygame.event.Event(pygame.QUIT)]]
        keys = [{pygame.K_LEFT: False, pygame.K_RIGHT: value}
                for value in (True, True, True, False, False)]
        with patch('pygame.event.get', side_effect=events), \
             patch('pygame.key.get_pressed', side_effect=keys), \
             patch('pygame.key.get_focused', return_value=True), \
             patch('pygame.quit'):
            game = runpy.run_path(str(ROOT/'src/circus.py'))
        self.assertEqual(game['active_character'].name, 'Knife thrower')
        self.assertEqual(game['acrobat'].animation.state, 'idle')
        self.assertFalse(game['acrobat'].keys_pressed['right'])
        self.assertEqual(game['knife_man'].rect.x, 254)


if __name__ == '__main__':
    unittest.main()
