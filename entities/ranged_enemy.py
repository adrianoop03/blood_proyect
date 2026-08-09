import pygame
import math
import random
from entities.enemy_utils import has_line_of_sight, move_towards
from entities.enemy_bullet import EnemyBullet


class RangedEnemy(pygame.sprite.Sprite):

    PATROL = "patrol"
    CHASE = "chase"
    KITE = "kite"

    def __init__(self, x, y, patrol_radius=150, manager=None):
        super().__init__()
        self.width = 30
        self.height = 30
        self.color = (60, 90, 200)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height))

        self.position = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=self.position)

        self.spawn_position = pygame.Vector2(x, y)
        self.patrol_radius = patrol_radius
        self.patrol_target = self.get_new_patrol_point()
        self.patrol_wait = 0

        self.speed = 100
        self.chase_speed = 140

        self.max_health = 25
        self.health = self.max_health

        self.detection_radius = 450
        self.lose_sight_radius = 600

        self.preferred_min_range = 280
        self.preferred_max_range = 420

        self.attack_damage = 8
        self.attack_cooldown = 0.7
        self.attack_timer = 0

        self.state = RangedEnemy.PATROL

        self.bullets = pygame.sprite.Group()

        self.manager = manager

        self.flash_timer = 0
        self.flash_duration = 0.15

    def get_new_patrol_point(self):
        angle = random.uniform(0, 360)
        dist = random.uniform(0, self.patrol_radius)
        offset = pygame.Vector2(
            math.cos(math.radians(angle)) * dist,
            math.sin(math.radians(angle)) * dist
        )
        return self.spawn_position + offset

    def update(self, dt, player, collision_rects, all_enemies=None):
        distance_to_player = self.position.distance_to(player.position)

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.attack_timer > 0:
            self.attack_timer -= dt

        # --- transiciones ---
        if self.state == RangedEnemy.PATROL:
            if distance_to_player <= self.detection_radius and has_line_of_sight(self.position, player.position, collision_rects):
                self.state = RangedEnemy.CHASE

        elif self.state in (RangedEnemy.CHASE, RangedEnemy.KITE):
            if distance_to_player > self.lose_sight_radius or not has_line_of_sight(self.position, player.position, collision_rects):
                self.state = RangedEnemy.PATROL
                self.patrol_target = self.get_new_patrol_point()

        # --- comportamiento ---
        if self.state == RangedEnemy.PATROL:
            if self.position.distance_to(self.patrol_target) < 10:
                self.patrol_wait -= dt
                if self.patrol_wait <= 0:
                    self.patrol_target = self.get_new_patrol_point()
                    self.patrol_wait = random.uniform(1.5, 3.0)
            else:
                self.position = move_towards(self.position, self.rect, self.patrol_target, self.speed, dt, collision_rects)
                self.rect.center = self.position

        elif self.state in (RangedEnemy.CHASE, RangedEnemy.KITE):
            if distance_to_player < self.preferred_min_range:
                # muy cerca: retrocede (kiting)
                direction_away = self.position - player.position
                if direction_away.length_squared() > 0:
                    direction_away = direction_away.normalize()
                retreat_target = self.position + direction_away * 200
                self.position = move_towards(self.position, self.rect, retreat_target, self.chase_speed, dt, collision_rects)
                self.rect.center = self.position
                self.state = RangedEnemy.KITE

            elif distance_to_player > self.preferred_max_range:
                # muy lejos: se acerca
                self.position = move_towards(self.position, self.rect, player.position, self.chase_speed, dt, collision_rects)
                self.rect.center = self.position
                self.state = RangedEnemy.CHASE

            else:
                # en rango ideal: dispara si tiene linea de vision
                self.state = RangedEnemy.KITE
                if has_line_of_sight(self.position, player.position, collision_rects) and self.attack_timer <= 0:
                    self.shoot(player)
                    self.attack_timer = self.attack_cooldown

        self.bullets.update(dt, collision_rects)

    def shoot(self, player):
        direction = player.position - self.position
        if direction.length_squared() > 0:
            direction = direction.normalize()
        new_bullet = EnemyBullet(self.position.x, self.position.y, direction, damage=self.attack_damage)
        self.bullets.add(new_bullet)

    def take_damage(self, amount):
        self.health -= amount
        self.flash_timer = self.flash_duration
        if self.health <= 0:
            self.kill()

    def draw(self, screen, camera):
        screen_pos = self.position - camera.position

        if self.flash_timer > 0:
            flash_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(flash_image, (255, 255, 255), (0, 0, self.width, self.height))
            draw_rect = flash_image.get_rect(center=screen_pos)
            screen.blit(flash_image, draw_rect)
        else:
            draw_rect = self.image.get_rect(center=screen_pos)
            screen.blit(self.image, draw_rect)

        bar_width = 30
        bar_height = 4
        health_ratio = self.health / self.max_health
        bar_x = screen_pos.x - bar_width / 2
        bar_y = screen_pos.y - self.height / 2 - 10

        pygame.draw.rect(screen, (0, 0, 60), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (60, 120, 220), (bar_x, bar_y, bar_width * health_ratio, bar_height))

        for b in self.bullets:
            b.draw(screen, camera)
