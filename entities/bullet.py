import pygame
import os

class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=25):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load("assets/images/bulletPH.png").convert_alpha(), (10, 20)
        )
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