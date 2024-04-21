import pygame
import random
from colors import colors
from Characters import *
from tiles_cotroller import get_tile, load_tilesheet
pygame.init()
WIDTH = 800
HEIGTH = 600
window = pygame.display.set_mode([WIDTH, HEIGTH])
pygame.display.set_caption("Circus lost in time")
timer = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont('Arial', 24)
acrobat = Acrobat("../img/acrobat_char_sprite.png", (100, 400), 10)
knife_man = KnifeThrower("../img/knife_man_sprite.png", (250, 400), 4)
strong_man = Strongman("../img/strong_man_char_sprite.png", (350,400), 2)
load_tilesheet()
example_tile = get_tile(0, 0)

# Lista kaikista hahmoista
characters = [acrobat, knife_man, strong_man]

# Määritä aktiivinen hahmo
active_character_index = 0
active_character = characters[active_character_index]

def draw_active_character_name():
    font = pygame.font.SysFont('Arial', 24)
    text = font.render(f"Active character: {active_character.name}", True, pygame.Color('black'))
    window.blit(text, (10, 10))  # Piirretään teksti ikkunan yläkulmaan


# game loop

run = True
while run:
    timer.tick(fps)
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
            elif event.key == pygame.K_LEFT:
                active_character.keys_pressed['left'] = True
            elif event.key == pygame.K_RIGHT:
                active_character.keys_pressed['right'] = True
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                active_character.keys_pressed['left'] = False
                active_character.keys_pressed['right'] = False

    # Liikuta ja päivitä aktiivinen hahmo
    active_character.move()
    active_character.update()

    # Piirrä kaikki hahmot näytölle
    for character in characters:
        window.blit(character.image, character.rect)

    draw_active_character_name()
    pygame.display.flip()

pygame.quit()