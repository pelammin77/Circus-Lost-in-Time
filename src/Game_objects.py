import pygame

def load_image(image_path):
    try:
        image = pygame.image.load(image_path).convert_alpha()
    except pygame.error as error:
        print(f"Cannot load image at {image_path}: {error}")
        return None
    return image

class Ground(pygame.sprite.Sprite):
    def __init__(self, image_path, position):
        super().__init__()
        self.image = load_image(image_path)
        self.rect = self.image.get_rect(topleft=position)

class GrassGround(Ground):
    def __init__(self, image_path, position):
        super().__init__(image_path, position)

class Floor(Ground):
    def __init__(self, image_path, position, durability):
        super().__init__(image_path, position)
        self.durability = durability

class WoodFloor(Floor):
    def __init__(self, image_path, position):
        super().__init__(image_path, position, durability=100)

class SteelFloor(Floor):
    def __init__(self, image_path, position):
        super().__init__(image_path, position, durability=200)

class StoneFloor(Floor):
    def __init__(self, image_path, position):
        super().__init__(image_path, position, durability=200)

class Wall(pygame.sprite.Sprite):
    def __init__(self, image_path, position, durability):
        super().__init__(image_path, position)
        self.image = load_image(image_path)
        self.rect = self.image.get_rect(topleft=position)
        self.durability = durability

class StoneWall(Wall):
    def __init__(self, image_path, position):
        super().__init__(image_path, position, durability=300)

class SteelWall(Wall):
    def __init__(self, image_path, position):
        super().__init__(image_path, position, durability=200)

class WoodWall(Wall):
    def __init__(self, image_path, position):
        super().__init__(image_path, position, durability=100)


class Ladder(pygame.sprite.Sprite):
    def __init__(self, image_path, position):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=position)


class Finish(pygame.sprite.Sprite): #maali mihin hahmojen on pyrittävä

    def __init__(self, image_path, position):
        super().__init__()
        self.image = load_image(image_path)
        self.rect = self.image.get_rect(topleft=position)