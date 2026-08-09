import pygame
from entities.player import Player
from world.level import *
from patterns.strategy.camera import Camera
from entities.bullet import bullet
from patterns.observer.hud import HUD
from entities.enemy import Enemy
from entities.ranged_enemy import RangedEnemy
from entities.enemy_manager import EnemyManager
from patterns.observer.skill_board import SkillBoard
from entities.upgrades import get_upgrade_pool
camera = Camera(1920, 1080)
pygame.init()
icon_image = pygame.image.load('core/game_icon.png')
pygame.display.set_icon(icon_image)
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Damn Beast")
clock = pygame.time.Clock()

player = Player()
hud=HUD()
level = Level(
    "assets/maps/level1.tmx"
)

level.spawn_player(player)
skill_board = SkillBoard(1920, 1080)
upgrade_pool = get_upgrade_pool()
enemy_positions = level.generate_enemy_spawns(count=30, player_position=player.position)

enemy_manager = EnemyManager(max_concurrent_attackers=3)

current_wave = 1
enemies_per_wave = 6

awaiting_wave_spawn = False

def spawn_wave(wave_number):
    count = enemies_per_wave + wave_number * 2
    positions = level.generate_enemy_spawns(count=count, player_position=player.position)
    group = pygame.sprite.Group()
    for i, pos in enumerate(positions):
        if i % 3 == 0:
            group.add(RangedEnemy(pos.x, pos.y, manager=enemy_manager))
        else:
            group.add(Enemy(pos.x, pos.y, manager=enemy_manager))
    return group


enemies = spawn_wave(current_wave)
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and skill_board.active:
            skill_board.handle_key(event.key, player)

    dt = clock.tick(60) / 1000

    player.update(
        dt,
        camera,
        level.collision.rects
    )
    if not skill_board.active:
    
        if awaiting_wave_spawn:
            enemies = spawn_wave(current_wave)
            awaiting_wave_spawn = False
    
            player.update(dt, camera, level.collision.rects)


        enemy_list = list(enemies)
        for enemy in enemies:
            enemy.update(dt, player, level.collision.rects, all_enemies=enemy_list)
                                 
        # impactos del jugador contra enemigos
        for enemy in enemies:
            hits = pygame.sprite.spritecollide(enemy, player.bullets, True)
            for hit in hits:
                enemy.take_damage(20)

        # impactos del enemigo contra el jugador 
        for enemy in enemies:
            if isinstance(enemy, RangedEnemy):
                for eb in list(enemy.bullets):
                    if eb.rect.colliderect(player.rect if hasattr(player, "rect") else pygame.Rect(player.position.x - 16, player.position.y - 16, 32, 32)):
                        player.take_damage(eb.damage)
                        eb.kill()
        # termina la oleada
        if len(enemies) == 0 and not awaiting_wave_spawn:
            current_wave += 1
            skill_board.open(upgrade_pool, count=3)
            awaiting_wave_spawn = True

    screen.fill((40, 40, 40))
    level.tilemap.draw(screen, camera)
    player.draw(screen, camera)

    for enemy in enemies:
        enemy.draw(screen, camera)

    if skill_board.active:
            skill_board.draw(screen)
    
    hud.draw(screen,player)
    camera.update(player, dt)
    pygame.display.flip()
    

pygame.quit()