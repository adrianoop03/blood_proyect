import pygame
import math
import random
from entities.enemy_utils import has_line_of_sight, move_towards


class Enemy(pygame.sprite.Sprite):

    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    RETREAT = "retreat"

    def __init__(self, x, y, patrol_radius=150, manager=None):
        super().__init__()
        self.width = 32
        self.height = 32
        self.color = (180, 40, 40)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height))

        self.position = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=self.position)

        self.spawn_position = pygame.Vector2(x, y)
        self.patrol_radius = patrol_radius
        self.patrol_target = self.get_new_patrol_point()
        self.patrol_wait = 0

        self.speed = 120
        self.chase_speed = 180

        self.max_health = 40
        self.health = self.max_health

        self.detection_radius = 350
        self.lose_sight_radius = 500
        self.attack_range = 45

        self.attack_damage = 10
        self.attack_cooldown = 1.2
        self.attack_timer = 0

        self.retreat_timer = 0
        self.retreat_duration = 0.4
        self.retreat_distance = 30

        self.state = Enemy.PATROL

        # --- coordinacion grupal ---
        self.manager = manager

        # --- feedback visual de daño ---
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

        # --- transiciones de estado ---
        if self.state == Enemy.PATROL:
            if distance_to_player <= self.detection_radius and has_line_of_sight(self.position, player.position, collision_rects):
                self.state = Enemy.CHASE

        elif self.state == Enemy.CHASE:
            if distance_to_player > self.lose_sight_radius or not has_line_of_sight(self.position, player.position, collision_rects):
                self.state = Enemy.PATROL
                self.patrol_target = self.get_new_patrol_point()
                if self.manager:
                    self.manager.release(self)

        elif self.state == Enemy.ATTACK:
            if distance_to_player > self.attack_range * 1.3:
                self.state = Enemy.CHASE
                if self.manager:
                    self.manager.release(self)

        elif self.state == Enemy.RETREAT:
            if self.retreat_timer <= 0:
                self.state = Enemy.CHASE

        # --- comportamiento segun estado ---
        if self.state == Enemy.PATROL:
            if self.position.distance_to(self.patrol_target) < 10:
                self.patrol_wait -= dt
                if self.patrol_wait <= 0:
                    self.patrol_target = self.get_new_patrol_point()
                    self.patrol_wait = random.uniform(1.5, 3.0)
            else:
                self.position = move_towards(self.position, self.rect, self.patrol_target, self.speed, dt, collision_rects)
                self.rect.center = self.position

        elif self.state == Enemy.CHASE:
            can_engage = distance_to_player <= self.attack_range
            granted = self.manager.request_engage(self) if self.manager else True

            if can_engage and granted:
                self.state = Enemy.ATTACK
                self.attack_timer = 0
            elif can_engage and not granted and all_enemies is not None:
                # ya esta en rango pero no le toca atacar: rodea al jugador
                slot_angle = self.manager.get_slot_angle(self, all_enemies)
                offset = pygame.Vector2(
                    math.cos(math.radians(slot_angle)),
                    math.sin(math.radians(slot_angle))
                ) * (self.attack_range * 1.6)
                surround_target = player.position + offset
                self.position = move_towards(self.position, self.rect, surround_target, self.chase_speed, dt, collision_rects)
                self.rect.center = self.position
            else:
                self.position = move_towards(self.position, self.rect, player.position, self.chase_speed, dt, collision_rects)
                self.rect.center = self.position

        elif self.state == Enemy.ATTACK:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                player.take_damage(self.attack_damage)
                self.attack_timer = self.attack_cooldown
                self.state = Enemy.RETREAT
                self.retreat_timer = self.retreat_duration
                if self.manager:
                    self.manager.release(self)

        elif self.state == Enemy.RETREAT:
            self.retreat_timer -= dt
            direction_away = self.position - player.position
            if direction_away.length_squared() > 0:
                direction_away = direction_away.normalize()
            retreat_target = self.position + direction_away * self.retreat_distance
            self.position = move_towards(self.position, self.rect, retreat_target, self.chase_speed, dt, collision_rects)
            self.rect.center = self.position

    def take_damage(self, amount):
        self.health -= amount
        self.flash_timer = self.flash_duration
        if self.health <= 0:
            if self.manager:
                self.manager.release(self)
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

        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
