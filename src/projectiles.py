"""Visual throwing knife: time-based flight and spin, no hit/damage logic."""
from pathlib import Path
import pygame
from collisions import collision_rect


class FlyingKnife(pygame.sprite.Sprite):
    def __init__(self, position, facing, bounds=(800,600), obstacles=()):
        super().__init__()
        self.base = pygame.image.load(str(Path(__file__).resolve().parent.parent/'img'/'throwing_knife.png')).convert_alpha()
        if facing < 0:
            self.base = pygame.transform.flip(self.base,True,False)
        self.position = pygame.Vector2(position)
        self.facing = facing
        self.age = 0.0
        self.obstacles=obstacles
        self.stuck_to=None
        self.stuck_age=0.0
        self.bounds = pygame.Rect(0,0,*bounds)
        self.image = self.base
        self.rect = self.image.get_rect(center=position)

    def update(self, dt):
        dt = max(0.0,dt)
        self.age += dt
        if self.stuck_to is not None:
            self.stuck_age+=dt
            self.position=pygame.Vector2(self.stuck_to.rect.topleft)+self.stuck_offset
            self.rect=self.image.get_rect(center=self.position)
            if self.stuck_age>=1: self.kill()
            return
        old_x=self.position.x
        self.position.x += self.facing*360*dt
        hits=[]
        for crate in self.obstacles:
            area=collision_rect(crate).inflate(20,20)
            if area.top<=self.position.y<=area.bottom:
                entry=max(old_x,area.left) if self.facing>0 else min(old_x,area.right)
                if min(old_x,self.position.x)<=entry<=max(old_x,self.position.x) and area.left<=entry<=area.right:
                    hits.append((abs(entry-old_x),entry,crate))
        if hits:
            _,x,crate=min(hits,key=lambda hit:hit[0])
            self.position.x=x
            self.stuck_to=crate
            self.stuck_offset=self.position-pygame.Vector2(crate.rect.topleft)
            self.image=self.base
            self.rect=self.image.get_rect(center=self.position)
            return
        # Eight discrete orientations keep the original pixel-art character.
        angle = -self.facing*(int(self.age*16)%8)*45
        self.image = pygame.transform.rotate(self.base,angle)
        self.rect = self.image.get_rect(center=(round(self.position.x),round(self.position.y)))
        if self.age >= 3 or not self.bounds.colliderect(self.rect):
            self.kill()
