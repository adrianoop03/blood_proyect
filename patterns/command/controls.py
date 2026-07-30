import pygame
from entities.bullet import *
class Controls:

    def get_direction(self):
        keys = pygame.key.get_pressed()

        movement = pygame.Vector2()

        if keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_d]:
            movement.x += 1
        if keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_s]:
            movement.y += 1
        if movement.length_squared() > 0:
            movement = movement.normalize()
        return movement
    
    def get_mouse_position(self):
        return pygame.mouse.get_pos()

    def is_shooting(self):
        keys = pygame.key.get_pressed()
        return pygame.mouse.get_pressed()[2]

    def is_running(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_LSHIFT]