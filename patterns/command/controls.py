import pygame


class Controls:

    def __init__(self):
        self.prev_healing = False

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
        return pygame.mouse.get_pressed()[0]

    def is_running(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_LSHIFT]

    def is_healing(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_e]

    def is_healing_just_pressed(self):
        keys = pygame.key.get_pressed()
        current = keys[pygame.K_e]
        just_pressed = current and not self.prev_healing
        self.prev_healing = current
        return just_pressed
