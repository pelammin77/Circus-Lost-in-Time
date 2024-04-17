import pygame

pygame.init()

WIDTH = 800
HEIGTH = 600
window = pygame.display.set_mode([WIDTH, HEIGTH])
pygame.display.set_caption("Circus lost in time")
timer = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont('Arial', 24)

# game loop

run = True
while run:
    timer.tick(fps)
    window.fill("blue")
    for event in pygame.event.get():
       if event.type == pygame.QUIT:
           run = False

    pygame.display.flip()
pygame.quit()