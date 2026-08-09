import pytmx
import pygame

class Collision:


            
    def move(self, entity, movement, walls):

        # Movimiento horizontal
        entity.hitbox.x += movement.x

        for wall in walls:
            if entity.hitbox.colliderect(wall):
                if movement.x > 0:
                    entity.hitbox.right = wall.left
                elif movement.x < 0:
                    entity.hitbox.left = wall.right

        # Movimiento vertical
        entity.hitbox.y += movement.y

        for wall in walls:
            if entity.hitbox.colliderect(wall):
                if movement.y > 0:
                    entity.hitbox.bottom = wall.top
                elif movement.y < 0:
                    entity.hitbox.top = wall.bottom

        entity.position.update(entity.hitbox.center)
