
import pygame

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

    def move(self):
        if self.keys_pressed["left"]:
            self.rect.x -= self.speed
            self.rect.x = max(self.rect.x, 0)  # Estä hahmoa menemästä ruudun vasemman reunan yli
        if self.keys_pressed["right"]:
            self.rect.x += self.speed
            self.rect.x = min(self.rect.x, self.win_width - self.rect.width)  # Estä hahmoa menemästä ruudun oikean reunan yli
    def update(self):
        # Tähän voi lisätä päivityslogiikkaa, kuten törmäysten tarkistuksen
        pass


    def action(self):
        pass



class Acrobat(Character):
    def __init__(self, image_path, position, speed):
        super().__init__(image_path, position, speed)
        self.jump_speed = 10
        self.gravity = 1
        self.name = "Acrobat"

    def jump(self):
        # Toteuta hyppytoiminto
        if not self.is_action:
            print("Jumping!")
            self.is_action = True
            self.vertical_velocity = -self.jump_speed



    def action(self):
        self.jump()

    def update(self):
        if self.is_action:
            self.rect.y += self.vertical_velocity
            self.vertical_velocity += self.gravity
            if self.rect.y >= 530:  # Tarkistetaan, onko hahmo maassa
                self.rect.y = 530
                self.is_action = False

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
