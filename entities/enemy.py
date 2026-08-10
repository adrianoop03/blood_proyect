import pygame
import math
import random
from entities.enemy_utils import has_line_of_sight, move_towards
from patterns.strategy.enemy_animator import EnemyAnimator

class Enemy(pygame.sprite.Sprite):

    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    RETREAT = "retreat"

    def __init__(self, x, y, patrol_radius=150, manager=None):
        super().__init__()
        self.width = 32
        self.height = 32

        self.position = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.position
        self.animator = EnemyAnimator("assets/images/drunk", "idle_armed")
        self.move_angle = -90
        self.hurt_timer = 0
        self.hurt_duration = 0.2
        self.is_dying = False
        self._attack_toggle = False

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
        self.blood_decals = None

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
            
        moving = False

        # --- comportamiento segun estado ---
        if self.state == Enemy.PATROL:
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

        elif self.state == Enemy.CHASE:
            can_engage = distance_to_player <= self.attack_range
            granted = self.manager.request_engage(self) if self.manager else True

            if can_engage and granted:
                self._face_towards(player.position)
                self.state = Enemy.ATTACK
                self.attack_timer = 0
                self._attack_toggle = not self._attack_toggle
                self.animator.play("attack2" if self._attack_toggle else "attack1")
            elif can_engage and not granted and all_enemies is not None:
                # ya esta en rango pero no le toca atacar: rodea al jugador
                slot_angle = self.manager.get_slot_angle(self, all_enemies)
                offset = pygame.Vector2(
                    math.cos(math.radians(slot_angle)),
                    math.sin(math.radians(slot_angle))
                ) * (self.attack_range * 1.6)
                surround_target = player.position + offset
                self._face_towards(player.position)
                self.position = move_towards(self.position, self.rect, player.position, self.chase_speed, dt, collision_rects)
                self.rect.center = self.position
                moving = True
            else:
                self._face_towards(player.position)
                self.position = move_towards(self.position, self.rect, player.position, self.chase_speed, dt, collision_rects)
                self.rect.center = self.position
                moving = True

        elif self.state == Enemy.ATTACK:
            self._face_towards(player.position)
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                player.take_damage(self.attack_damage)
                self.attack_timer = self.attack_cooldown
                self.state = Enemy.RETREAT
                self.retreat_timer = self.retreat_duration
                if self.manager:
                    self.manager.release(self)

        elif self.state == Enemy.RETREAT:
            self._face_towards(player.position)
            self.retreat_timer -= dt
            direction_away = self.position - player.position
            if direction_away.length_squared() > 0:
                direction_away = direction_away.normalize()
            retreat_target = self.position + direction_away * self.retreat_distance
            self.position = move_towards(self.position, self.rect, retreat_target, self.chase_speed, dt, collision_rects)
            self.rect.center = self.position
            moving = True

        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        elif self.state != Enemy.ATTACK:
            self.animator.play("walk" if moving else "idle_armed")

        self.animator.update(dt)

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
            if self.manager:
                self.manager.release(self)
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


        if self.is_dying:
            return

        bar_width = 30
        bar_height = 4
        health_ratio = self.health / self.max_health
        bar_x = screen_pos.x - bar_width / 2
        bar_y = screen_pos.y - self.height / 2 - 10

        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
