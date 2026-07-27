import pygame
import os
import math
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

        self.aim_angle = -90
        self.aim_target_angle = -90
        self.move_direction = pygame.Vector2(0, -1)
        self.target_angle = -90
        self.rotation_speed = 1080  # grados por segundo

        

    def update(self, dt, camera, collision_rects):

        direction = self.controls.get_direction()
        
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
        #  disparo 
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        if self.controls.is_shooting() and self.shoot_cooldown <= 0:
            shoot_direction = pygame.Vector2(
            math.cos(math.radians(self.aim_angle + 90)),
            math.sin(math.radians(self.aim_angle + 90))
    )
            new_bullet = bullet(self.position.x, self.position.y, shoot_direction)
            self.bullets.add(new_bullet)
            self.shoot_cooldown = self.shoot_delay

        self.bullets.update(dt,collision_rects)


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
        

        
        screen.blit(body, body_rect)
        screen.blit(head, head_rect)
        # --- dibujar balas con offset de cámara ---
        for b in self.bullets:
            bullet_rect = b.image.get_rect(center=b.position - camera.position)
            screen.blit(b.image, bullet_rect)