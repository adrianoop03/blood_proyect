import pygame
import os
import math
from patterns.command.controls import Controls
from patterns.strategy.movement import Movement
from patterns.strategy.aim import Aim
from patterns.strategy.animator import Animator
from patterns.strategy.rotator import Rotator
from world.collision import Collision
class Player:
    def __init__(self):
        self.healing = False
        self.position = pygame.Vector2(0, 0)
        self.controls = Controls()
        self.movement = Movement()
        self.aim = Aim()
        self.rotator = Rotator()
        self.animator = Animator(
            "assets/images/player",
            "idleAr",
        )
        self.speed = 400
        self.move_angle = -90
        self.move_target_angle = -90

        self.aim_angle = -90
        self.aim_target_angle = -90
        self.move_direction = pygame.Vector2(0, -1)
        self.target_angle = -90
        self.rotation_speed = 1080  # grados por segundo

        # Sistema de colisiones
        self.collision = Collision()

        # Hitbox del jugador
        self.hitbox = pygame.Rect(0, 0, 80, 80)
        self.hitbox.center = self.position

        
    def start_healing(self):
        self.healing = True

        self.animator.play_body("healing")
        self.animator.play_head("healing")
    def update(self, dt, camera, walls):

        direction = self.controls.get_direction()
        
        movement, moving = self.movement.move(
            self,
            direction,
            dt
        )
        self.collision.move(
            self,
            movement,
            walls
        )

        mouse_world = camera.screen_to_world(
            pygame.mouse.get_pos()
        )

        self.aim.update(
            self,
            mouse_world
        )

        if self.controls.is_healing_just_pressed() and not self.healing:
            self.start_healing()
        if self.healing:
            if self.animator.body_player.finished:
                self.healing = False

        if moving:
            aim_direction = pygame.Vector2(
                math.cos(math.radians(self.aim_angle + 90)),
                math.sin(math.radians(self.aim_angle + 90))
            )

            dot = self.move_direction.dot(aim_direction)

            if dot >= 0:
                self.animator.play_legs("frontwalk")
                if not self.healing:
                    self.animator.play_body("frontwalk")
                    self.animator.play_head("frontwalk")
            else:
                self.animator.play_legs("backwalk")
                if not self.healing:
                    self.animator.play_body("backwalk")
                    self.animator.play_head("backwalk")
        else:
            self.animator.play_legs("idleAr")
            if not self.healing:
                self.animator.play_body("idleAr")
                self.animator.play_head("idleAr")


        self.animator.update(dt)

        self.rotator.update(self, dt)

        self.hitbox.center = (
            int(self.position.x),
            int(self.position.y)
        )
        
        
    def draw(self, screen, camera):
        screen_position = camera.world_to_screen(self.position)
        if self.animator.legs_player.animation == "frontwalk":
            legs = pygame.transform.rotate(
                self.animator.legs,
                -self.move_angle
            )
            legs_rect = legs.get_rect(center=self.position - camera.position)
            screen.blit(legs, legs_rect)
        elif self.animator.legs_player.animation == "backwalk":
            legs = pygame.transform.rotate(
                self.animator.legs,
                -(self.move_angle + 180)
            )
            legs_rect = legs.get_rect(center=self.position - camera.position)
            screen.blit(legs, legs_rect)
        else:
            legs = pygame.transform.rotate(
                self.animator.legs,
                -self.aim_angle
            )
            legs_rect = legs.get_rect(center=self.position - camera.position)
            screen.blit(legs, legs_rect)
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