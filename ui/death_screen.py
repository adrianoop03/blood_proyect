import pygame
from utils.helpers import Button, load_font
from database.score_repository import ScoreRepository


class DeathScreen:

    OPTIONS = ["Reintentar", "Volver al Menú"]
    MAX_NAME_LENGTH = 16

    def __init__(self, screen, score=0):
        self.screen = screen
        self.score = score
        self.repository = ScoreRepository()
        self.name = ""
        self.saved = False

        self.title_font = load_font(90)
        self.subtitle_font = load_font(34)
        self.score_font = load_font(38)
        self.input_font = load_font(38)
        self.button_font = load_font(40)

        center_x = screen.get_width() // 2
        start_y = 520
        spacing = 110
        button_width, button_height = 380, 80

        self.input_box = pygame.Rect(center_x - 220, 400, 440, 64)

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
        # escribir el nombre mientras no se haya guardado el puntaje
        if event.type == pygame.KEYDOWN and not self.saved:
            if event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.key == pygame.K_RETURN:
                self._save()
            elif event.unicode.isprintable() and len(self.name) < self.MAX_NAME_LENGTH:
                self.name += event.unicode

        for label, button in self.buttons:
            if button.is_clicked(event):
                if not self.saved:
                    self._save()  # guarda con el nombre tipeado (o "Jugador" si esta vacio)
                return label

        return None

    def _save(self):
        self.repository.save_score(self.name, self.score)
        self.saved = True

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for _, button in self.buttons:
            button.update(mouse_pos)

    def draw(self):
        screen = self.screen
        screen.fill((20, 15, 15))  # mismo tono oscuro que el menu, con un toque rojizo

        title = self.title_font.render("HAS CAÍDO", True, (170, 30, 30))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 160))
        screen.blit(title, title_rect)

        subtitle = self.subtitle_font.render("La bestia te ha reclamado", True, (150, 130, 130))
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 220))
        screen.blit(subtitle, subtitle_rect)

        score_label = self.score_font.render(f"Puntaje: {self.score}", True, (230, 230, 230))
        score_rect = score_label.get_rect(center=(screen.get_width() // 2, 300))
        screen.blit(score_label, score_rect)

        if self.saved:
            info_label = self.subtitle_font.render(
                "Puntaje guardado en el ranking", True, (150, 190, 150)
            )
            info_rect = info_label.get_rect(center=(screen.get_width() // 2, 360))
            screen.blit(info_label, info_rect)
        else:
            hint_label = self.subtitle_font.render(
                "Escribi tu nombre para guardar el puntaje:", True, (200, 190, 190)
            )
            hint_rect = hint_label.get_rect(center=(screen.get_width() // 2, 360))
            screen.blit(hint_label, hint_rect)

            pygame.draw.rect(screen, (45, 30, 30), self.input_box, border_radius=8)
            pygame.draw.rect(screen, (170, 30, 30), self.input_box, width=2, border_radius=8)

            name_surface = self.input_font.render(self.name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(
                midleft=(self.input_box.x + 16, self.input_box.centery)
            )
            screen.blit(name_surface, name_rect)

        for _, button in self.buttons:
            button.draw(screen)