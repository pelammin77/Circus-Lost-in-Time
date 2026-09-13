import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
from pathlib import Path
import sys
import unittest
import pygame
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from Characters import KnifeThrower
from projectiles import FlyingKnife


class ProjectileTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800,600))

    def tearDown(self):
        pygame.quit()

    def test_release_once_and_repeat(self):
        a=KnifeThrower(str(ROOT/'img/knife_man_sprite.png'),(250,400),4)
        a.action()
        a.update(.23)
        self.assertEqual(len(a.projectiles),0)
        a.update(.01)
        self.assertEqual(len(a.projectiles),1)
        knife=next(iter(a.projectiles))
        self.assertAlmostEqual(knife.position.x,a.rect.left+69)
        a.action()
        a.update(.24)
        self.assertEqual(len(a.projectiles),1)
        a.action()
        a.update(.24)
        self.assertEqual(len(a.projectiles),2)

    def test_direction_spin_and_cleanup(self):
        for facing in (-1,1):
            knife=FlyingKnife((400,300),facing)
            group=pygame.sprite.Group(knife)
            before=pygame.image.tobytes(knife.image,'RGBA')
            knife.update(.1)
            self.assertAlmostEqual(knife.position.x,400+36*facing)
            self.assertEqual(knife.position.y,300)
            self.assertNotEqual(before,pygame.image.tobytes(knife.image,'RGBA'))
            group.update(3)
            self.assertEqual(len(group),0)

    def test_large_dt_release_and_time_step_consistency(self):
        actors=[KnifeThrower(str(ROOT/'img/knife_man_sprite.png'),(250,400),4) for _ in range(2)]
        for a in actors: a.action()
        actors[0].update(.4)
        for _ in range(40): actors[1].update(.01)
        for a in actors: self.assertEqual(len(a.projectiles),1)
        self.assertAlmostEqual(next(iter(actors[0].projectiles)).position.x,
                               next(iter(actors[1].projectiles)).position.x)
