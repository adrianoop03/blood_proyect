import pygame

class HUD:

    def __init__(self):
        self.health_empty = pygame.image.load("assets/ui/bars/life_bar_empty.png").convert_alpha()
        self.health_full = pygame.image.load("assets/ui/bars/life_bar.png").convert_alpha()

        self.stamina_empty = pygame.image.load("assets/ui/bars/stamina_bar_empty.png").convert_alpha()
        self.stamina_full = pygame.image.load("assets/ui/bars/stamina_bar.png").convert_alpha()

        self.x = 20
        self.y = 20
        self.spacing = 10

    def draw(self, screen, player):
        # barra de vida vacía 
        screen.blit(self.health_empty, (self.x, self.y))

        # recorte de la barra de vida llena según %  
        health_ratio = player.health / player.max_health
        bar_width = self.health_full.get_width()
        visible_width = int(bar_width * health_ratio)

        if visible_width > 0:
            crop_rect = pygame.Rect(0, 0, visible_width, self.health_full.get_height())
            screen.blit(self.health_full, (self.x, self.y), crop_rect)
        #  stamina 
        stamina_y = self.y + self.health_full.get_height() + self.spacing
        screen.blit(self.stamina_empty, (self.x, stamina_y))

        energy_ratio = player.energy / player.max_energy
        stamina_width = self.stamina_full.get_width()
        visible_stamina_width = int(stamina_width * energy_ratio)

        if visible_stamina_width > 0:
            crop_rect = pygame.Rect(0, 0, visible_stamina_width, self.stamina_full.get_height())
            screen.blit(self.stamina_full, (self.x, stamina_y), crop_rect)