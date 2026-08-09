import pygame


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=14, damage=8, color=(255, 140, 40), radius=5):
        super().__init__()

        diameter = radius * 2
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)

        self.position = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=self.position)
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.lifetime = 3.0

    def update(self, dt, collision_rects):
        self.position += self.direction * self.speed
        self.rect.center = self.position

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        if self.rect.collidelist(collision_rects) != -1:
            self.kill()

    def draw(self, screen, camera):
        screen_pos = self.position - camera.position
        draw_rect = self.image.get_rect(center=screen_pos)
        screen.blit(self.image, draw_rect)
