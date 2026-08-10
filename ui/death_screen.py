import pygame
from utils.helpers import Button, load_font


class DeathScreen:

    OPTIONS = ["Reintentar", "Volver al Menú"]

    def __init__(self, screen):
        self.screen = screen

        self.title_font = load_font(90)
        self.subtitle_font = load_font(34)
        self.button_font = load_font(40)

        center_x = screen.get_width() // 2
        start_y = 460
        spacing = 110
        button_width, button_height = 380, 80

        self.buttons = []
        for i, label in enumerate(self.OPTIONS):
            rect = (
                center_x - button_width // 2,
                start_y + i * spacing,
                button_width,
                button_height,
            )
            self.buttons.append((label, Button(
                rect, label, self.button_font,
                base_color=(230, 230, 230),
                hover_color=(200, 40, 40)  # hover rojo en vez de dorado, tono de muerte
            )))

    def handle_event(self, event):
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
        screen.fill((20, 15, 15))  # mismo tono oscuro que el menu, con un toque rojizo

        title = self.title_font.render("HAS CAÍDO", True, (170, 30, 30))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 220))
        screen.blit(title, title_rect)

        subtitle = self.subtitle_font.render("La bestia te ha reclamado", True, (150, 130, 130))
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 320))
        screen.blit(subtitle, subtitle_rect)

        for _, button in self.buttons:
            button.draw(screen)
