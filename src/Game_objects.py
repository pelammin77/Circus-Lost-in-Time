import pygame

class Floor(pygame.sprite.Sprite):
    def __init__(self, image_path, position):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=position)

class WoodFloor(Floor):
    def __init__(self, position):
        super().__init__("path_to_wood_floor_image.png", position)
        self.durability = 100  # Oletuskestävyys puulattialle

class SteelFloor(Floor):
    def __init__(self, position):
        super().__init__("path_to_steel_floor_image.png", position)
        self.durability = 200  # Oletuskestävyys teräslattialle


class StoneFloor(Floor):
    def __init__(self, position):
        super().__init__("path_to_steel_floor_image.png", position)
        self.durability = 200  # Oletuskestävyys teräslattialle



class Ground(pygame.sprite.Sprite):
    def __init__(self, image_path, position):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=position)

class GrassGround(Ground):
    def __init__(self, position):
        super().__init__("path_to_grass_ground_image.png", position)

class Wall(pygame.sprite.Sprite):
    def __init__(self, image_path, position):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=position)

class StoneWall(Wall):
    def __init__(self, position):
        super().__init__("", position)
        self.durability = 300  # Oletuskestävyys puulattialle

class SteelWall(Wall):
    def __init__(self, position):
        super().__init__("", position)
        self.durability = 200  # Oletuskestävyys puulattialle

class WoodWall(Wall):
    def __init__(self, position):
        super().__init__("", position)
        self.durability = 100  # Oletuskestävyys puulattialle



class Ladder(pygame.sprite.Sprite):
    def __init__(self, image_path, position):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=position)