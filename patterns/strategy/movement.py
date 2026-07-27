import pygame
import math 

class Movement:

    def move(self, player, direction, dt):

        if direction.length_squared() == 0:
            player.move_target_angle = player.aim_target_angle
            return pygame.Vector2(), False

        direction = direction.normalize()

        player.move_direction = direction

        player.move_target_angle = (
            math.degrees(math.atan2(direction.y, direction.x))
            - 90
        )

        movement = direction * player.speed * dt

        return movement, True