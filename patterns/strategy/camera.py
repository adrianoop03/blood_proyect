import pygame

class Camera:

    def __init__(self, width, height):

        self.position = pygame.Vector2(0, 0)

        self.width = width 
        self.height = height 

        self.follow_speed = 8
        
    def update(self, player, dt):

        mx, my = pygame.mouse.get_pos()

        mouse_screen = pygame.Vector2(mx, my)

        direction = (
            mouse_screen
            - pygame.Vector2(self.width/2, self.height/2)
        )

        target = (
            player.position
            + direction * 0.25
            - pygame.Vector2(self.width/2, self.height/2)
        )

        self.position = self.position.lerp(
            target,
            min(self.follow_speed * dt, 1)
        )
    def world_to_screen(self, position):
        return position - self.position
    def screen_to_world(self, screen_position):
        return pygame.Vector2(screen_position) + self.position