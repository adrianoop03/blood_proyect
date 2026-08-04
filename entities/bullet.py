import pygame
import os

class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=18,radius=4,color =(255,0,0)):
        super().__init__()
        diameter = radius * 2
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)

        self.position = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=self.position)
        self.direction = direction
        self.speed = speed
        self.lifetime = 2.0

    def update(self, dt ,collision_rects):
        self.position += self.direction * self.speed
        self.rect.center = self.position

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        if self.rect.collidelist(collision_rects) != -1:
            self.kill()