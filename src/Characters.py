
import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, image_path, position, speed):
        super().__init__()
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=position)
        self.speed = speed

    def move(self, direction):
        if direction == 'up':
            self.rect.y -= self.speed
        elif direction == 'down':
            self.rect.y += self.speed
        elif direction == 'left':
            self.rect.x -= self.speed
        elif direction == 'right':
            self.rect.x += self.speed

    def update(self):
        # Tähän voi lisätä päivityslogiikkaa, kuten törmäysten tarkistuksen
        pass



class Acrobat(Character):
    def jump(self):
        # Toteuta hyppytoiminto
        print("Jumping!")

class KnifeThrower(Character):
    def throw_knife(self):
        # Toteuta veitsenheitto
        print("Throwing a knife!")

class Strongman(Character):
    def lift(self):
        # Toteuta nostotoiminto
        print("Lifting!")
