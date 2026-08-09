import pygame
from patterns.state.state import State
from utils.helpers import Button


class OptionsState(State):
    """Pantalla de opciones. Placeholder simple: se puede ampliar cuando
    haya un ConfigRepository / config.py con valores persistentes."""

    def __init__(self, game):
        super().__init__(game)

        self.title_font = pygame.font.SysFont("arialblack", 70)
        self.label_font = pygame.font.SysFont("arial", 40)
        self.button_font = pygame.font.SysFont("arial", 36)

        self.volume = 0.5

        center_x = self.game.screen.get_width() // 2

        self.volume_down_button = Button(
            (center_x - 220, 400, 80, 70), "-", self.button_font
        )
        self.volume_up_button = Button(
            (center_x + 140, 400, 80, 70), "+", self.button_font
        )

        self.back_button = Button(
            (60, 60, 220, 70), "Volver", self.button_font
        )

    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            from patterns.state.menu_state import MenuState
            self.game.state_manager.set_state(MenuState(self.game))
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from patterns.state.menu_state import MenuState
            self.game.state_manager.set_state(MenuState(self.game))
            return

        if self.volume_down_button.is_clicked(event):
            self.volume = max(0.0, self.volume - 0.1)
            pygame.mixer.music.set_volume(self.volume)

        if self.volume_up_button.is_clicked(event):
            self.volume = min(1.0, self.volume + 0.1)
            pygame.mixer.music.set_volume(self.volume)

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.volume_down_button.update(mouse_pos)
        self.volume_up_button.update(mouse_pos)
        self.back_button.update(mouse_pos)

    def draw(self, screen):
        screen.fill((25, 25, 35))

        title = self.title_font.render("OPCIONES", True, (230, 200, 60))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 200))
        screen.blit(title, title_rect)

        volume_label = self.label_font.render(
            f"Volumen: {int(self.volume * 100)}%", True, (230, 230, 230)
        )
        volume_rect = volume_label.get_rect(
            center=(screen.get_width() // 2, 340)
        )
        screen.blit(volume_label, volume_rect)

        self.volume_down_button.draw(screen)
        self.volume_up_button.draw(screen)
        self.back_button.draw(screen)
