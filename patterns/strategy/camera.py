import pygame

class Camera:
    def __init__(self, width, height):
        self.position = pygame.Vector2(0, 0)
        self.width = width
        self.height = height
        self.follow_speed = 8
        self.zoom = 1.0 
        
    def snap_to(self, player):
        self.position = (
            player.position
            - pygame.Vector2(self.view_width / 2, self.view_height / 2)
        )

    @property
    def view_width(self):
        return self.width / self.zoom

    @property
    def view_height(self):
        return self.height / self.zoom

    def update(self, player, dt):
        mx, my = pygame.mouse.get_pos()
        mouse_screen = pygame.Vector2(mx, my)

        direction = mouse_screen - pygame.Vector2(self.width / 2, self.height / 2)

        target = (
            player.position
            + direction * 0.25
            - pygame.Vector2(self.view_width / 2, self.view_height / 2)
        )

        self.position = self.position.lerp(target, min(self.follow_speed * dt, 1))

    def world_to_screen(self, position):
        return position - self.position

    def screen_to_world(self, screen_position):
        scale_x = self.view_width / self.width
        scale_y = self.view_height / self.height

        scaled = pygame.Vector2(
            screen_position[0] * scale_x,
            screen_position[1] * scale_y
        )
        return scaled + self.position
    