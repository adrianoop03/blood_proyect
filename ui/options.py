import pygame
from utils.helpers import Button, load_font

RESOLUTIONS = [(1920, 1080), (1600, 900), (1280, 720)]


class Options:
    #opcines 
    #volumen
    def __init__(self, screen, volume=0.5):
        self.screen = screen

        self.title_font = load_font(70)
        self.label_font = load_font(36)
        self.button_font = load_font(34)

        self.volume = volume

        current_size = screen.get_size()
        self.res_index = RESOLUTIONS.index(current_size) if current_size in RESOLUTIONS else 0
        self.fullscreen = bool(screen.get_flags() & pygame.FULLSCREEN)

        self.needs_apply = False
        self.pending_settings = None

        center_x = screen.get_width() // 2

        self.volume_down_button = Button((center_x - 220, 320, 80, 70), "-", self.button_font)
        self.volume_up_button = Button((center_x + 140, 320, 80, 70), "+", self.button_font)

        self.resolution_button = Button(
            (center_x - 260, 440, 520, 70), self._resolution_label(), self.button_font
        )
        self.fullscreen_button = Button(
            (center_x - 260, 540, 520, 70), self._fullscreen_label(), self.button_font
        )

        self.apply_button = Button((center_x - 260, 660, 240, 70), "Aplicar", self.button_font)
        self.back_button = Button((center_x + 20, 660, 240, 70), "Volver", self.button_font)
    #resolucion
    def _resolution_label(self):
        w, h = RESOLUTIONS[self.res_index]
        return f"Resolucion: {w}x{h}"
    #pnatlla completa
    def _fullscreen_label(self):
        return f"Pantalla completa: {'Si' if self.fullscreen else 'No'}"
    #botn volver a menu principal
    def handle_event(self, event):
        
        if self.back_button.is_clicked(event):
            return "Volver"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "Volver"

        if self.volume_down_button.is_clicked(event):
            self.volume = max(0.0, self.volume - 0.1)
            pygame.mixer.music.set_volume(self.volume)

        if self.volume_up_button.is_clicked(event):
            self.volume = min(1.0, self.volume + 0.1)
            pygame.mixer.music.set_volume(self.volume)

        if self.resolution_button.is_clicked(event):
            self.res_index = (self.res_index + 1) % len(RESOLUTIONS)
            self.resolution_button.text = self._resolution_label()

        if self.fullscreen_button.is_clicked(event):
            self.fullscreen = not self.fullscreen
            self.fullscreen_button.text = self._fullscreen_label()

        if self.apply_button.is_clicked(event):
            w, h = RESOLUTIONS[self.res_index]
            self.needs_apply = True
            self.pending_settings = (w, h, self.fullscreen)

        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.volume_down_button.update(mouse_pos)
        self.volume_up_button.update(mouse_pos)
        self.resolution_button.update(mouse_pos)
        self.fullscreen_button.update(mouse_pos)
        self.apply_button.update(mouse_pos)
        self.back_button.update(mouse_pos)

    def draw(self):
        screen = self.screen
        screen.fill((25, 25, 35))

        title = self.title_font.render("OPCIONES", True, (230, 200, 60))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 200))
        screen.blit(title, title_rect)

        volume_label = self.label_font.render(
            f"Volumen: {int(self.volume * 100)}%", True, (230, 230, 230)
        )
        volume_rect = volume_label.get_rect(center=(screen.get_width() // 2, 280))
        screen.blit(volume_label, volume_rect)

        self.volume_down_button.draw(screen)
        self.volume_up_button.draw(screen)
        self.resolution_button.draw(screen)
        self.fullscreen_button.draw(screen)
        self.apply_button.draw(screen)
        self.back_button.draw(screen)