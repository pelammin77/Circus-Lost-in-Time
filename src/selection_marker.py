"""Small arrow above the currently controlled character."""
import pygame


class SelectionMarker:
    def draw(self,surface,character):
        head_y=character.rect.top
        if getattr(character,'carried',None):
            head_y=min(head_y,character.carried.rect.top)
        x=max(6,min(character.rect.centerx,surface.get_width()-7))
        y=max(4,head_y-13)
        pygame.draw.polygon(surface,(26,30,43),[(x-5,y),(x+5,y),(x,y+7)])
        pygame.draw.polygon(surface,(255,224,94),[(x-3,y+1),(x+3,y+1),(x,y+5)])
