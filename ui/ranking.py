import pygame
from utils.helpers import Button, load_font
from database.score_repository import ScoreRepository


class Ranking:
    """Pantalla que muestra el top de puntajes guardados en SQLite."""

    def __init__(self, screen):
        self.screen = screen

        self.title_font = load_font(70)
        self.row_font = load_font(34)
        self.button_font = load_font(36)

        self.repository = ScoreRepository()
        self.scores = self.repository.get_top_scores(10)

        center_x = screen.get_width() // 2
        self.back_button = Button(
            (center_x - 130, screen.get_height() - 140, 260, 70),
            "Volver",
            self.button_font,
        )

    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            return "Volver"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "Volver"
        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(mouse_pos)

    def draw(self):
        screen = self.screen
        screen.fill((25, 25, 35))

        title = self.title_font.render("RANKING", True, (230, 200, 60))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 140))
        screen.blit(title, title_rect)

        center_x = screen.get_width() // 2

        if not self.scores:
            empty_label = self.row_font.render(
                "Todavia no hay puntajes guardados", True, (200, 200, 200)
            )
            empty_rect = empty_label.get_rect(center=(center_x, 300))
            screen.blit(empty_label, empty_rect)
        else:
            start_y = 250
            spacing = 56

            for i, row in enumerate(self.scores):
                position = i + 1
                color = (230, 200, 60) if position <= 3 else (230, 230, 230)

                name_text = f"{position}.  {row['player_name']}"
                score_text = str(row["score"])

                name_label = self.row_font.render(name_text, True, color)
                score_label = self.row_font.render(score_text, True, color)

                y = start_y + i * spacing

                screen.blit(name_label, (center_x - 320, y))
                score_rect = score_label.get_rect(topright=(center_x + 320, y))
                screen.blit(score_label, score_rect)

        self.back_button.draw(screen)