"""Small movable demo prop, independent of the unfinished level system."""
from pathlib import Path
import pygame


class CircusCrate(pygame.sprite.Sprite):
    def __init__(self, midbottom):
        super().__init__()
        self.image=pygame.image.load(str(Path(__file__).resolve().parent.parent/'img'/'circus_crate.png')).convert_alpha()
        self.rect=self.image.get_rect(midbottom=midbottom)
        self.holder=None
