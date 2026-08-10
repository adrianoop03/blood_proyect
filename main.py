import pygame

from entities.player import Player
from entities.bullet import bullet
from entities.enemy import Enemy
from entities.ranged_enemy import RangedEnemy
from entities.enemy_manager import EnemyManager
from entities.upgrades import get_upgrade_pool

from world.level import *

from patterns.strategy.camera import Camera
from patterns.observer.hud import HUD
from patterns.observer.skill_board import SkillBoard
from patterns.decorator.blood import BloodDecals

from managers.sound_manager import SoundManager

from ui.menu import Menu
from ui.options import Options
from ui.pause import Pause
from ui.death_screen import DeathScreen
from ui.ranking import Ranking

from utils.helpers import load_font

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

icon_image = pygame.image.load("core/game_icon.png")
pygame.display.set_icon(icon_image)

screen = pygame.display.set_mode(
    (1920, 1080),
    pygame.FULLSCREEN | pygame.SCALED
)

pygame.display.set_caption("Damn Beast")
clock = pygame.time.Clock()

score_font = load_font(34)


# "menu"

current_screen = "menu"

menu = Menu(screen)
ranking = None
options = None
pause = None
death_screen = None

camera = None
player = None
level = None

score = 0

hud = None
blood_decals = None
sound_manager = None
skill_board = None
upgrade_pool = None
enemy_manager = None
enemies = pygame.sprite.Group()

current_wave = 1
enemies_per_wave = 6

awaiting_wave_spawn = False


def spawn_wave(wave_number):
    count = enemies_per_wave + wave_number * 2

    positions = level.generate_enemy_spawns(
        count=count,
        player_position=player.position
    )

    group = pygame.sprite.Group()

    for i, pos in enumerate(positions):
        if i % 3 == 0:
            group.add(
                RangedEnemy(
                    pos.x,
                    pos.y,
                    manager=enemy_manager
                )
            )
        else:
            group.add(
                Enemy(
                    pos.x,
                    pos.y,
                    manager=enemy_manager
                )
            )

    return group


running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if current_screen == "menu":

            selection = menu.handle_event(event)

            if selection == "Iniciar":

                camera = Camera(
                    screen.get_width(),
                    screen.get_height()
                )

                player = Player()

                sound_manager = SoundManager()
                player.sound_manager = sound_manager

                hud = HUD()

                level = Level(
                    "assets/maps/level2.tmx"
                )

                level.spawn_player(player)

                blood_decals = BloodDecals(
                    level_size=(level.width, level.height)
                )

                player.blood_decals = blood_decals   # una sola vez, antes del loop

                skill_board = SkillBoard(
                    screen.get_width(),
                    screen.get_height()
                )

                upgrade_pool = get_upgrade_pool()

                enemy_manager = EnemyManager(
                    max_concurrent_attackers=3
                )

                current_wave = 1
                awaiting_wave_spawn = False

                score = 0

                enemies = spawn_wave(current_wave)

                current_screen = "juego"

            elif selection == "Ranking":

                ranking = Ranking(screen)
                current_screen = "ranking"

            elif selection == "Opciones":

                options = Options(screen)
                current_screen = "opciones"

            elif selection == "Salir":

                running = False

        elif current_screen == "juego":

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:

                pause = Pause(screen)
                current_screen = "pausa"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_k:

                player.take_damage(10)  # tecla de debug para probar el sistema de daño

                print(
                    f"Jugador recibió daño, vida actual: {player.health}"
                )

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:

                curo = player.try_heal()

                if curo:
                    print(
                        f"Jugador se curo. Vida: {player.health}, cargas restantes: {player.heal_charges}"
                    )
                else:
                    print("No se pudo curar (sin cargas o vida llena)")

            if event.type == pygame.KEYDOWN and skill_board.active:

                skill_board.handle_key(
                    event.key,
                    player
                )

        elif current_screen == "pausa":

            selection = pause.handle_event(event)

            if selection == "Continuar":

                current_screen = "juego"

            elif selection == "Volver al Menu":

                current_screen = "menu"

            elif selection == "Salir":

                running = False


        elif current_screen == "opciones":

            if options.handle_event(event) == "Volver":

                current_screen = "menu"

        elif current_screen == "ranking":

            if ranking.handle_event(event) == "Volver":

                current_screen = "menu"

        elif current_screen == "muerte":

            selection = death_screen.handle_event(event)

            if selection == "Reintentar":
                camera = Camera(screen.get_width(), screen.get_height())
                player = Player()
                sound_manager = SoundManager()
                player.sound_manager = sound_manager
                hud = HUD()
                level = Level("assets/maps/level2.tmx")
                level.spawn_player(player)
                blood_decals = BloodDecals(level_size=(level.width, level.height))
                player.blood_decals = blood_decals
                skill_board = SkillBoard(screen.get_width(), screen.get_height())
                upgrade_pool = get_upgrade_pool()
                enemy_manager = EnemyManager(max_concurrent_attackers=3)
                current_wave = 1
                awaiting_wave_spawn = False
                score = 0
                enemies = spawn_wave(current_wave)
                current_screen = "juego"

            elif selection == "Volver al Menú":
                current_screen = "menu"

    # opcines manejo de ventana y resolucion

    if current_screen == "opciones" and options.needs_apply:

        width, height, fullscreen = options.pending_settings

        flags = pygame.FULLSCREEN if fullscreen else 0

        screen = pygame.display.set_mode(
            (width, height),
            flags
        )

        menu = Menu(screen)

        options = Options(
            screen,
            volume=options.volume
        )

        if pause is not None:
            pause = Pause(screen)

        if ranking is not None:
            ranking = Ranking(screen)

        if death_screen is not None:
            death_screen = DeathScreen(screen, score)

    if current_screen == "juego":

        if not skill_board.active:

            if awaiting_wave_spawn:

                enemies = spawn_wave(current_wave)

                awaiting_wave_spawn = False

            player.update(
                dt,
                camera,
                level.collisionmap.rects,
                enemies
            )

            if player.is_dead and player.animator.body_player.finished:
                death_screen = DeathScreen(screen, score)
                current_screen = "muerte"
            camera.update(
                player,
                dt
            )

            enemy_list = list(enemies)

            for enemy in enemies:

                enemy.update(
                    dt,
                    player,
                    level.collisionmap.rects,
                    all_enemies=enemy_list
                )

            # impactos del jugador contra enemigos

            for enemy in enemies:

                hits = pygame.sprite.spritecollide(
                    enemy,
                    player.bullets,
                    True
                )

                for hit in hits:

                    enemy.take_damage(20)

                    if enemy.health <= 0:

                        score += 100

            # impactos del enemigo contra el jugador

            for enemy in enemies:

                if isinstance(enemy, RangedEnemy):

                    for eb in list(enemy.bullets):

                        if hasattr(player, "rect"):

                            player_rect = player.rect

                        else:

                            player_rect = pygame.Rect(
                                player.position.x - 16,
                                player.position.y - 16,
                                32,
                                32
                            )

                        if eb.rect.colliderect(player_rect):

                            player.take_damage(eb.damage)

                            eb.kill()

            # termina la oleada

            if len(enemies) == 0 and not awaiting_wave_spawn:

                current_wave += 1

                skill_board.open(
                    upgrade_pool,
                    count=3
                )

                awaiting_wave_spawn = True

    if current_screen == "menu":

        menu.update()
        menu.draw()

    elif current_screen == "juego":

        screen.fill((40, 40, 40))

        level.tilemap.draw(
            screen,
            camera
        )

        blood_decals.draw(
            screen,
            camera
        )

        player.draw(
            screen,
            camera
        )

        for enemy in enemies:

            enemy.draw(
                screen,
                camera
            )

        if skill_board.active:

            skill_board.draw(screen)

        hud.draw(
            screen,
            player
        )

        score_label = score_font.render(
            f"Puntaje: {score}", True, (230, 230, 230)
        )
        score_rect = score_label.get_rect(
            topright=(screen.get_width() - 30, 30)
        )
        screen.blit(score_label, score_rect)

    elif current_screen == "pausa":

        screen.fill((40, 40, 40))

        level.tilemap.draw(
            screen,
            camera
        )

        blood_decals.draw(
            screen,
            camera
        )

        player.draw(
            screen,
            camera
        )

        for enemy in enemies:

            enemy.draw(
                screen,
                camera
            )

        pause.update()
        pause.draw()

    elif current_screen == "opciones":

        options.update()
        options.draw()

    elif current_screen == "ranking":

        ranking.update()
        ranking.draw()

    elif current_screen == "muerte":

        death_screen.update()
        death_screen.draw()

    pygame.display.flip()


pygame.quit()