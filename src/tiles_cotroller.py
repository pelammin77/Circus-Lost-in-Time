import pygame

# Asetukset
TILE_SIZE = 32  # Oletetaan, että jokainen tiili on 32x32 pikseliä
TILESHEET_PATH = '../img/Assets.png'  # Oleta, että tämä on tilesheetisi polku

# Globaali muuttuja tilesheetille
tilesheet = None

def load_tilesheet():
    global tilesheet
    tilesheet = pygame.image.load(TILESHEET_PATH).convert_alpha()

# Funktio tiilien hakemiseen tilesheetistä
def get_tile(tile_x, tile_y):
    """Hae yksittäinen tiili sijainnista (tile_x, tile_y) tilesheetistä."""
    if not tilesheet:
        load_tilesheet()
    return tilesheet.subsurface(pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def create_level(level_map, tile_size):
    game_objects = pygame.sprite.Group()
    y = 0
    for row in level_map:
        x = 0
        for col in row:
            if col == '-':
                tile = GrassGround('path_to_grass_image.png', (x * tile_size, y * tile_size))
                game_objects.add(tile)
            elif col == '|':
                tile = Wall('path_to_wall_image.png', (x * tile_size, y * tile_size), durability=100)
                game_objects.add(tile)
            x += 1
        y += 1
    return game_objects
