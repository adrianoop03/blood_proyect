import pygame
from entities.player import Player
from world.level import *
from patterns.strategy.camera import Camera
from entities.bullet import bullet
from patterns.observer.hud import HUD
camera = Camera(1920, 1080)
pygame.init()
icon_image = pygame.image.load('core/game_icon.png')
pygame.display.set_icon(icon_image)
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Damn Beast")
clock = pygame.time.Clock()

<<<<<<< HEAD
# "menu" | "juego" | "pausa" | "ranking" | "opciones"
current_screen = "menu"

menu = Menu(screen)
ranking = None
options = None
pause = None

camera = None
player = None
level = None

running = True

while running:

    dt = clock.tick(60) / 1000

=======
player = Player()
hud=HUD()
level = Level(
    "assets/maps/level1.tmx"
)

level.spawn_player(player)
running = True
while running:

>>>>>>> origin/feature/lautarotonini
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(60) / 1000

    player.update(
        dt,
        camera,
        level.collision.rects
    )

    screen.fill((40,40,40))
    level.tilemap.draw(screen, camera)
    player.draw(screen, camera)
    hud.draw(screen,player)
    camera.update(player, dt)
    pygame.display.flip()
    

pygame.quit()