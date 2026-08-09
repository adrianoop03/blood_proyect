import pygame
from patterns.state.state import State
from utils.helpers import Button


class MenuState(State):
    """Menu principal: Iniciar, Ranking, Opciones y Salir."""

    def __init__(self, game):
        super().__init__(game)

        self.title_font = pygame.font.SysFont("arialblack", 90)
        self.button_font = pygame.font.SysFont("arial", 40)

        center_x = self.game.screen.get_width() // 2
        start_y = 420
        spacing = 110
        button_width, button_height = 380, 80

        labels = ["Iniciar", "Ranking", "Opciones", "Salir"]
        self.buttons = []
        for i, label in enumerate(labels):
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
                self._on_option_selected(label)

    def _on_option_selected(self, label):
        if label == "Iniciar":
            from patterns.state.playing_state import PlayingState
            self.game.state_manager.set_state(PlayingState(self.game))

        elif label == "Ranking":
            from patterns.state.ranking_state import RankingState
            self.game.state_manager.set_state(RankingState(self.game))

        elif label == "Opciones":
            from patterns.state.options_state import OptionsState
            self.game.state_manager.set_state(OptionsState(self.game))

        elif label == "Salir":
            self.game.quit()

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for _, button in self.buttons:
            button.update(mouse_pos)

    def draw(self, screen):
        screen.fill((25, 25, 35))

        title = self.title_font.render("DAMN BEAST", True, (230, 200, 60))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 220))
        screen.blit(title, title_rect)

        for _, button in self.buttons:
            button.draw(screen)
