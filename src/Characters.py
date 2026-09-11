
import pygame
from pathlib import Path
from animation import SpriteAnimation

class Character(pygame.sprite.Sprite):
    def __init__(self, image_path, position, speed, width=800):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=position)
        self.speed =  speed #speed
        self.win_width = width
        self.keys_pressed = {"left": False, "right": False}
        self.is_action = False
        self.name = ""
        self.animation = None
        self.facing = 1
        self.is_moving = False

    def move(self):
        previous_x = self.rect.x
        direction = int(self.keys_pressed['right']) - int(self.keys_pressed['left'])
        self.rect.x += direction * self.speed
        self.rect.x = max(0, min(self.rect.x, self.win_width - self.rect.width))
        self.is_moving = self.rect.x != previous_x
        if self.is_moving:
            self.facing = 1 if self.rect.x > previous_x else -1

    def update(self, dt=1/60):
        if self.animation:
            self.image = self.animation.frame(self.animation_state(), dt, self.facing)

    def animation_state(self):
        return 'walk' if self.is_moving else 'idle'


    def action(self):
        pass



class Acrobat(Character):
    def __init__(self, image_path, position, speed):
        super().__init__(image_path, position, speed)
        self.jump_speed = 10
        self.gravity = 1
        self.vertical_velocity = 0
        self.landing_remaining = 0.0
        self.name = "Acrobat"
        self.animation = SpriteAnimation(
            Path(__file__).resolve().parent.parent / 'img' / 'acrobat_animations.png',
            (48, 64), {'idle': (0, (0, 1, 2, 3, 2, 1), 4), 'walk': (1, (0, 1, 2, 3), 8),
                       'rise': (2, (0,), 1), 'apex': (2, (1,), 1),
                       'fall': (2, (2,), 1), 'land': (2, (3,), 1)})
        self.image = self.animation.frame('idle', 0)
        # Keep the original foot position when changing to a padded frame.
        feet = self.rect.midbottom
        self.rect = self.image.get_rect(midbottom=(feet[0], feet[1]+2))

    def jump(self):
        # Toteuta hyppytoiminto
        if not self.is_action:
            print("Jumping!")
            self.is_action = True
            self.jump_start_y = self.rect.y
            self.vertical_velocity = -self.jump_speed
            self.landing_remaining = 0.0

    def animation_state(self):
        if self.is_action:
            if abs(self.vertical_velocity) <= 2:
                return 'apex'
            return 'rise' if self.vertical_velocity < 0 else 'fall'
        if self.landing_remaining > 0:
            return 'land'
        return super().animation_state()



    def action(self):
        self.jump()

    def update(self, dt=1/60):
        self.landing_remaining = max(0.0, self.landing_remaining - max(0.0, dt))
        if self.is_action:
            self.rect.y += self.vertical_velocity
            self.vertical_velocity += self.gravity
            if self.vertical_velocity >= 0 and self.rect.y >= self.jump_start_y:
                self.rect.y = self.jump_start_y
                self.is_action = False
                self.vertical_velocity = 0
                self.landing_remaining = 0.08
        super().update(dt)

class KnifeThrower(Character):
    def __init__(self, image_path, position, speed):
        super().__init__(image_path, position, speed)
        self.name = "Knife thrower"

    def throw_knife(self):
        # Toteuta veitsenheitto
        print("Throwing a knife!")

    def action(self):
        self.throw_knife()


class Strongman(Character):
    def __init__(self, image_path, position, speed):
        super().__init__(image_path, position, speed)
        self.name = "Strong man"


    def lift(self):
        # Toteuta nostotoiminto
        print("Lifting!")

    def action(self):
        self.lift()
