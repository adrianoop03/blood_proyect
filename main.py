import pygame

from entities.player import Player
from world.level import *
from patterns.strategy.camera import Camera
from entities.bullet import bullet
from patterns.observer.hud import HUD
from patterns.decorator.blood import BloodDecals
from entities.enemy import Enemy
from entities.ranged_enemy import RangedEnemy
from entities.enemy_manager import EnemyManager
from managers.sound_manager import SoundManager
camera = Camera(1920, 1080)
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
icon_image = pygame.image.load('core/game_icon.png')
pygame.display.set_icon(icon_image)
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Damn Beast")
clock = pygame.time.Clock()
player = Player()
sound_manager = SoundManager()
player.sound_manager = sound_manager
hud = HUD()
level = Level(
    "assets/maps/level1.tmx"
)
blood_decals = BloodDecals(level_size=(level.width, level.height))
player.blood_decals = blood_decals   # una sola vez, antes del loop
level.spawn_player(player)
enemy_positions = level.generate_enemy_spawns(count=30, player_position=player.position)

enemy_manager = EnemyManager(max_concurrent_attackers=3)

enemies = pygame.sprite.Group()
for i, pos in enumerate(enemy_positions):
    if i % 3 == 0:
        enemies.add(RangedEnemy(pos.x, pos.y, manager=enemy_manager))
    else:
        enemies.add(Enemy(pos.x, pos.y, manager=enemy_manager))
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
        level.collisionmap.rects,
        enemies
    )
    enemy_list = list(enemies)
    for enemy in enemies:
        enemy.update(dt, player, level.collisionmap.rects, all_enemies=enemy_list)

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

    screen.fill((40, 40, 40))
    level.tilemap.draw(screen, camera)
    blood_decals.draw(screen, camera)
    player.draw(screen, camera)
    hud.draw(screen, player)

    for enemy in enemies:
        enemy.draw(screen, camera)


    
    hud.draw(screen,player)
    camera.update(player, dt)
    pygame.display.flip()

pygame.quit()
