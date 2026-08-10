import pygame
import math
import random
from entities.enemy_utils import has_line_of_sight, move_towards
from entities.enemy_bullet import EnemyBullet
from patterns.strategy.enemy_animator import EnemyAnimator


class RangedEnemy(pygame.sprite.Sprite):

    PATROL = "patrol"
    CHASE = "chase"
    KITE = "kite"

    def __init__(self, x, y, patrol_radius=150, manager=None):
        super().__init__()
        self.width = 30
        self.height = 30

        self.position = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.position

        self.animator = EnemyAnimator("assets/images/drunk", "idle_armed")
        self.move_angle = -90
        self.hurt_timer = 0
        self.hurt_duration = 0.2
        self.is_dying = False

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
        self.blood_decals = None

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

    def _face_towards(self, target):
        direction = target - self.position
        if direction.length_squared() > 0:
            self.move_angle = math.degrees(math.atan2(direction.y, direction.x)) - 90

    def update(self, dt, player, collision_rects, all_enemies=None):
        distance_to_player = self.position.distance_to(player.position)

        if self.flash_timer > 0:
            self.flash_timer -= dt

        if player.position.x != self.position.x:
            self.facing_right = player.position.x >= self.position.x

        if self.is_dying:
            self.animator.update(dt)
            if self.animator.finished:
                self.kill()
            return

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

        moving = False
        shooting = False

        # --- comportamiento ---
        if self.state == RangedEnemy.PATROL:
            if self.position.distance_to(self.patrol_target) < 10:
                self.patrol_wait -= dt
                if self.patrol_wait <= 0:
                    self.patrol_target = self.get_new_patrol_point()
                    self.patrol_wait = random.uniform(1.5, 3.0)
            else:
                self._face_towards(self.patrol_target)
                self.position = move_towards(self.position, self.rect, self.patrol_target, self.speed, dt, collision_rects)
                self.rect.center = self.position
                moving = True

        elif self.state in (RangedEnemy.CHASE, RangedEnemy.KITE):
            if distance_to_player < self.preferred_min_range:
                # muy cerca: retrocede (kiting)
                direction_away = self.position - player.position
                if direction_away.length_squared() > 0:
                    direction_away = direction_away.normalize()
                retreat_target = self.position + direction_away * 200
                self._face_towards(player.position) 
                self.position = move_towards(self.position, self.rect, retreat_target, self.chase_speed, dt, collision_rects)
                self.rect.center = self.position
                self.state = RangedEnemy.KITE
                moving = True

            elif distance_to_player > self.preferred_max_range:
                # muy lejos: se acerca
                self._face_towards(player.position)
                self.position = move_towards(self.position, self.rect, player.position, self.chase_speed, dt, collision_rects)
                self.rect.center = self.position
                self.state = RangedEnemy.CHASE
                moving = True

            else:
                # en rango ideal: dispara si tiene linea de vision
                self._face_towards(player.position)
                self.state = RangedEnemy.KITE
                if has_line_of_sight(self.position, player.position, collision_rects) and self.attack_timer <= 0:
                    self.shoot(player)
                    self.attack_timer = self.attack_cooldown
                    shooting = True

        self.bullets.update(dt, collision_rects)

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        elif shooting:
            self.animator.play("attack1")
        else:
            self.animator.play("walk" if moving else "idle_armed")

        self.animator.update(dt)

    def shoot(self, player):
        direction = player.position - self.position
        if direction.length_squared() > 0:
            direction = direction.normalize()
        new_bullet = EnemyBullet(self.position.x, self.position.y, direction, damage=self.attack_damage)
        self.bullets.add(new_bullet)

    def take_damage(self, amount):
        if self.is_dying:
            return

        self.health -= amount
        self.flash_timer = self.flash_duration

        if self.blood_decals:
            self.blood_decals.splash_world(
                self.position,
                blood_type="enemy",
                avoid_rect=self.rect
            )

        if self.health <= 0:
            self.is_dying = True
            self.animator.play("die")
        else:
            self.hurt_timer = self.hurt_duration
            self.animator.play("hurt")

    def draw(self, screen, camera):
        screen_pos = self.position - camera.position

        legs = pygame.transform.rotate(self.animator.legs, -self.move_angle)
        body = pygame.transform.rotate(self.animator.torso, -self.move_angle)
        head = pygame.transform.rotate(self.animator.head, -self.move_angle)

        if self.flash_timer > 0:
            legs = legs.copy()
            legs.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
            body = body.copy()
            body.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
            head = head.copy()
            head.fill((255, 255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)

        screen.blit(legs, legs.get_rect(center=screen_pos))
        screen.blit(body, body.get_rect(center=screen_pos))
        screen.blit(head, head.get_rect(center=screen_pos))
        bar_width = 30
        bar_height = 4
        health_ratio = self.health / self.max_health
        bar_x = screen_pos.x - bar_width / 2
        bar_y = screen_pos.y - self.height / 2 - 10

        pygame.draw.rect(screen, (0, 0, 60), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (60, 120, 220), (bar_x, bar_y, bar_width * health_ratio, bar_height))

        for b in self.bullets:
            b.draw(screen, camera)

        if self.is_dying:
            return
