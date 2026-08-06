import pygame
from utils.helpers import Button, load_font


class Pause:
    

    OPTIONS = ["Continuar", "Volver al Menu", "Salir"]

    def __init__(self, screen):
        self.screen = screen

        self.title_font = load_font(70)
        self.button_font = load_font(38)

        center_x = screen.get_width() // 2
        start_y = 460
        spacing = 100
        button_width, button_height = 380, 80

        self.buttons = []
        for i, label in enumerate(self.OPTIONS):
            rect = (
                center_x - button_width // 2,
                start_y + i * spacing,
                button_width,
                button_height,
            )
            self.buttons.append((label, Button(rect, label, self.button_font)))

        self.overlay = pygame.Surface(
            (screen.get_width(), screen.get_height()), pygame.SRCALPHA
        )
        self.overlay.fill((0, 0, 0, 160))

    def handle_event(self, event):
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "Continuar"

        for label, button in self.buttons:
            if button.is_clicked(event):
                return label
        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for _, button in self.buttons:
            button.update(mouse_pos)

    def draw(self):
        screen = self.screen
        screen.blit(self.overlay, (0, 0))

        title = self.title_font.render("PAUSA", True, (230, 200, 60))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 300))
        screen.blit(title, title_rect)

        for _, button in self.buttons:
            button.draw(screen)