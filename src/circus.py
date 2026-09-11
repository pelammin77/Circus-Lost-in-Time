import pygame
import random
from pathlib import Path
from colors import colors
from Characters import *
from tiles_cotroller import get_tile, load_tilesheet
from Game_objects import *


def create_level(level_map, tile_size):
    game_objects = pygame.sprite.Group()
    y = 0
    for row in level_map:
        x = 0
        for col in row:
            if col == '-':
                tile = GrassGround('"../img/grass_ground.png"', (x * tile_size, y * tile_size))
                game_objects.add(tile)
            elif col == '|':
                tile = Wall('../img/ground_wall.png', (x * tile_ize, y * tile_size), durability=100)
                game_objects.add(tile)
            x += 1
        y += 1
    return game_objects




pygame.init()
WIDTH = 800
HEIGTH = 600
window = pygame.display.set_mode([WIDTH, HEIGTH])
pygame.display.set_caption("Circus lost in time")
timer = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont('Arial', 24)
ASSETS = Path(__file__).resolve().parent.parent / 'img'
acrobat = Acrobat(str(ASSETS / 'acrobat_char_sprite.png'), (100, 400), 10)
knife_man = KnifeThrower(str(ASSETS / 'knife_man_sprite.png'), (250, 400), 4)
strong_man = Strongman(str(ASSETS / 'strong_man_char_sprite.png'), (350,400), 2)
load_tilesheet()
example_tile = get_tile(0, 0)

# Lista kaikista hahmoista
characters = [acrobat, knife_man, strong_man]

# Määritä aktiivinen hahmo
active_character_index = 0
active_character = characters[active_character_index]


def create_characters(characters):
    pass

def draw(windows, characters, active_character):
    # Piirrä kaikki hahmot näytölle
    for character in characters:
        window.blit(character.image, character.rect)

    font = pygame.font.SysFont('Arial', 24)
    text = font.render(f"Active character: {active_character.name}", True, pygame.Color('black'))
    window.blit(text, (10, 10))  # Piirretään teksti ikkunan yläkulmaan

    pygame.display.flip()

def update(active_character, dt):
    # Inactive characters stop walking but their animation/physics keeps updating.
    for character in characters:
        character.is_moving = False
    active_character.move()
    for character in characters:
        character.update(dt)


# game loop

run = True
while run:
    dt = timer.tick(fps) / 1000.0
    window.fill(colors["sky_blue"])
    # Piirrä esimerkki tiili näytölle
    window.blit(example_tile, (100, 100))

    # Käsittele tapahtumia
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                active_character.action()
            elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                # Vaihda aktiivista hahmoa
                active_character_index = (active_character_index + 1) % len(characters)
                active_character = characters[active_character_index]



    pressed = pygame.key.get_pressed()
    focused = pygame.key.get_focused()
    for character in characters:
        character.keys_pressed['left'] = bool(focused and character is active_character and pressed[pygame.K_LEFT])
        character.keys_pressed['right'] = bool(focused and character is active_character and pressed[pygame.K_RIGHT])
    update(active_character, dt)
    draw(window, characters, active_character)


pygame.quit()
