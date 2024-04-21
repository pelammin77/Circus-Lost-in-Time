import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Level editor")

tile_size = 40
width, height = screen.get_size()
grid = [[0] * (width // tile_size) for _ in range(height // tile_size)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            grid[y // tile_size][x // tile_size] = 1

    screen.fill((0, 0, 0))
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if grid[y][x] == 1:
                pygame.draw.rect(screen, (255, 255, 255), (x * tile_size, y * tile_size, tile_size, tile_size))

    pygame.display.flip()

pygame.quit()
