import pygame
from utils.helpers import Button, load_font


class Menu:
    
#opciones menu
    OPTIONS = ["Iniciar", "Opciones", "Salir"]

    def __init__(self, screen):
        self.screen = screen

        self.title_font = load_font(90)
        self.button_font = load_font(40)

        center_x = screen.get_width() // 2
        start_y = 420
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
            self.buttons.append((label, Button(rect, label, self.button_font)))

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
        screen.fill((25, 25, 35))

        title = self.title_font.render("DAMN BEAST", True, (230, 200, 60))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 220))
        screen.blit(title, title_rect)

        for _, button in self.buttons:
            button.draw(screen)