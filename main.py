import pygame

from entities.player import Player
from world.level import *
from patterns.strategy.camera import Camera
from entities.bullet import bullet
from patterns.observer.hud import HUD
from patterns.decorator.blood import BloodDecals
camera = Camera(1920, 1080)
pygame.init()
icon_image = pygame.image.load('core/game_icon.png')
pygame.display.set_icon(icon_image)
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Damn Beast")
clock = pygame.time.Clock()

player = Player()
hud = HUD()
level = Level(
    "assets/maps/level1.tmx"
)
blood_decals = BloodDecals(level_size=(level.width, level.height))
player.blood_decals = blood_decals   # una sola vez, antes del loop
level.spawn_player(player)
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
            player.take_damage(10)  # tecla de debug para probar el sistema de daño
            print(f"Jugador recibió daño, vida actual: {player.health}")

    dt = clock.tick(60) / 1000

    player.update(
        dt,
        camera,
        level.collisionmap.rects
    )

    screen.fill((40, 40, 40))
    level.tilemap.draw(screen, camera)
    blood_decals.draw(screen, camera)
    player.draw(screen, camera)
    hud.draw(screen, player)
    camera.update(player, dt)
    pygame.display.flip()

pygame.quit()
