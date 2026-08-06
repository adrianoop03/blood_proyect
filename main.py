import pygame
from entities.player import Player
from world.level import *
from patterns.strategy.camera import Camera
from ui.menu import Menu

from ui.options import Options, RESOLUTIONS
from ui.pause import Pause

pygame.init()
icon_image = pygame.image.load('core/game_icon.png')
pygame.display.set_icon(icon_image)
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Damn Beast")
clock = pygame.time.Clock()

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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_screen == "menu":
            selection = menu.handle_event(event)

            if selection == "Iniciar":
                camera = Camera(screen.get_width(), screen.get_height())
                player = Player()
                level = Level("assets/maps/level1.tmx")
                level.spawn_player(player)
                current_screen = "juego"

           # elif selection == "Ranking":
            #    ranking = Ranking(screen)
             #   current_screen = "ranking"

            elif selection == "Opciones":
                options = Options(screen)
                current_screen = "opciones"

            elif selection == "Salir":
                running = False

        elif current_screen == "juego":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause = Pause(screen)
                current_screen = "pausa"

        elif current_screen == "pausa":
            selection = pause.handle_event(event)

            if selection == "Continuar":
                current_screen = "juego"

            elif selection == "Volver al Menu":
                current_screen = "menu"

            elif selection == "Salir":
                running = False

        elif current_screen == "ranking":
            if ranking.handle_event(event) == "Volver":
                current_screen = "menu"

        elif current_screen == "opciones":
            if options.handle_event(event) == "Volver":
                current_screen = "menu"

    # opcines manejo de ventana y resolucion
    if current_screen == "opciones" and options.needs_apply:
        width, height, fullscreen = options.pending_settings
        flags = pygame.FULLSCREEN if fullscreen else 0
        screen = pygame.display.set_mode((width, height), flags)

        menu = Menu(screen)
        options = Options(screen, volume=options.volume)

    if current_screen == "menu":
        menu.update()
        menu.draw()

    elif current_screen == "juego":
        player.update(
            dt,
            camera,
            level.collisionmap.rects
        )
        camera.update(player, dt)

        screen.fill((40, 40, 40))
        level.tilemap.draw(screen, camera)
        player.draw(screen, camera)

    elif current_screen == "pausa":
        screen.fill((40, 40, 40))
        level.tilemap.draw(screen, camera)
        player.draw(screen, camera)

        pause.update()
        pause.draw()

    elif current_screen == "ranking":
        ranking.update()
        ranking.draw()

    elif current_screen == "opciones":
        options.update()
        options.draw()

    pygame.display.flip()

pygame.quit()