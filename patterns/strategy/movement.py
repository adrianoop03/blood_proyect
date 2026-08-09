import pygame
import math 

class Movement:

    def move(self, player, direction, dt, collision_rects):

        if direction.length_squared() > 0:
            direction = direction.normalize()

            player.move_direction = direction

            player.move_target_angle = math.degrees(
                math.atan2(direction.y, direction.x)
            ) - 90

            # --- Movimiento con colisión, separado por eje ---
            width, height = 32, 32  # ajustá esto al tamaño real del sprite/hitbox

            # Eje X
            new_x = player.position.x + direction.x * player.speed * dt
            rect_x = pygame.Rect(0, 0, width, height)
            rect_x.center = (new_x, player.position.y)

            if not any(rect_x.colliderect(r) for r in collision_rects):
                player.position.x = new_x

            # Eje Y
            new_y = player.position.y + direction.y * player.speed * dt
            rect_y = pygame.Rect(0, 0, width, height)
            rect_y.center = (player.position.x, new_y)

            if not any(rect_y.colliderect(r) for r in collision_rects):
                player.position.y = new_y

            return True
        else:
            player.move_target_angle = player.aim_target_angle

        return False