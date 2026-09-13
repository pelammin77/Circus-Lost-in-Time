"""Visible solid ground and raised platform for the demo scene."""
import pygame

GROUND_TOP=540


class Platform:
    def __init__(self,rect):
        self.rect=pygame.Rect(rect)

    def draw(self,surface):
        pygame.draw.rect(surface,(91,66,54),self.rect)
        pygame.draw.rect(surface,(43,61,44),self.rect,2)
        pygame.draw.rect(surface,(72,132,62),(self.rect.x,self.rect.y,self.rect.width,5))
        pygame.draw.line(surface,(151,190,83),self.rect.topleft,(self.rect.right-1,self.rect.top),2)
        for x in range(self.rect.left+14,self.rect.right-4,28):
            if self.rect.height>10:
                pygame.draw.line(surface,(124,88,63),(x,self.rect.top+8),(x+8,self.rect.top+8),2)
