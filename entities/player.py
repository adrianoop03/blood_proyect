import pygame
import os
import math
import random
from entities.bullet import bullet
from patterns.command.controls import Controls
from patterns.strategy.movement import Movement
from patterns.strategy.aim import Aim
from patterns.strategy.animator import Animator
from patterns.strategy.rotator import Rotator
class Player:
    def __init__(self):
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0
        self.shoot_delay = 0.3 
        self.controls = Controls()
        self.movement = Movement()
        self.aim = Aim()
        self.rotator = Rotator()
        self.animator = Animator(
            "assets\images\player",
            "idleAr",
        )
        self.position = pygame.Vector2(400, 300)
        self.speed = 400
        self.move_angle = -90
        self.move_target_angle = -90

        # vida
        self.max_health = 100
        self.health = 100
        self.flash_timer = 0
        self.flash_duration = 0.15

        #  energía
        self.max_energy = 100
        self.energy = 100
        self.energy_regen_rate = 20   
        self.sprint_energy_cost = 30 

        self.base_speed = 400
        self.sprint_speed = 700
        self.speed = self.base_speed 

        self.aim_angle = -90
        self.aim_target_angle = -90
        self.move_direction = pygame.Vector2(0, -1)
        self.target_angle = -90
        self.rotation_speed = 1080  

        

    def update(self, dt, camera, collision_rects):

        direction = self.controls.get_direction()
        #  correr
        is_trying_to_run = self.controls.is_running() and direction.length_squared() > 0

        if is_trying_to_run and self.energy > 0:
            self.speed = self.sprint_speed
            self.energy -= self.sprint_energy_cost * dt
            if self.energy < 0:
                self.energy = 0
        else:
            self.speed = self.base_speed
            self.regen_energy(dt)
        
        moving = self.movement.move(self, direction, dt, collision_rects)

        mouse_world = camera.screen_to_world(
            pygame.mouse.get_pos()
        )

        self.aim.update(
            self,
            mouse_world
        )
        
        if moving:
            aim_direction = pygame.Vector2(
                math.cos(math.radians(self.aim_angle + 90)),
                math.sin(math.radians(self.aim_angle + 90))
            )

            dot = self.move_direction.dot(aim_direction)

            if dot >= 0:
                self.animator.play("frontwalk")
            else:
                self.animator.play("backwalk")
        else:
            self.animator.play("idleAr")
        
        self.animator.update(dt)

        self.rotator.update(self, dt)
        # disparo 
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        if self.controls.is_shooting() and self.shoot_cooldown <= 0:
            num_pellets = 6          # cantidad de perdigones
            spread_angle = 45        # angulo del cono de disparo

            for i in range(num_pellets):
                offset = random.uniform(-spread_angle / 2, spread_angle / 2)
                angle = self.aim_angle + 90 + offset

                shoot_direction = pygame.Vector2(
                    math.cos(math.radians(angle)),
                    math.sin(math.radians(angle))
                )

                new_bullet = bullet(self.position.x, self.position.y, shoot_direction)
                self.bullets.add(new_bullet)
            
            self.shoot_cooldown = self.shoot_delay
        self.bullets.update(dt, collision_rects)
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def draw(self, screen, camera):
        screen_position = camera.world_to_screen(self.position)

        if self.animator.current_animation == "frontwalk":
            feet = pygame.transform.rotate(
                self.animator.feet,
                -self.move_angle
            )
            feet_rect = feet.get_rect(center=self.position - camera.position)
            screen.blit(feet, feet_rect)
        elif self.animator.current_animation == "backwalk":
            feet = pygame.transform.rotate(
                self.animator.feet,
                -(self.move_angle + 180)
            )
            feet_rect = feet.get_rect(center=self.position - camera.position)
            screen.blit(feet, feet_rect)
        else:
            pass
        body = pygame.transform.rotate(
            self.animator.torso,
            -self.aim_angle
        )
        body_rect = body.get_rect(center=self.position - camera.position)
        
        head = pygame.transform.rotate(
            self.animator.head,
            -self.aim_angle
        )
        head_rect = head.get_rect(center=self.position - camera.position)
        

        
        if self.flash_timer > 0:
            flash_body = body.copy()
            flash_body.fill((255, 60, 60, 255), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(flash_body, body_rect)

            flash_head = head.copy()
            flash_head.fill((255, 60, 60, 255), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(flash_head, head_rect)
        else:
            screen.blit(body, body_rect)
            screen.blit(head, head_rect)

        # dibujar balas
        for b in self.bullets:
            bullet_rect = b.image.get_rect(center=b.position - camera.position)
            screen.blit(b.image, bullet_rect)

    def take_damage(self, amount):
        self.health -= amount
        self.flash_timer = self.flash_duration
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def regen_energy(self, dt):
        self.energy += self.energy_regen_rate * dt
        if self.energy > self.max_energy:
            self.energy = self.max_energy