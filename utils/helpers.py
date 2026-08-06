import pygame

FONT_PATH = "assets/fonts/Fleshandblood-MVA5x.ttf"


def load_font(size):
    return pygame.font.Font(FONT_PATH, size)


class Button:
    """Boton invisible: no dibuja recuadro ni fondo, solo el texto
    centrado en su area. El hover se nota porque el texto cambia de
    color al pasar el mouse por arriba."""

    def __init__(self, rect, text, font,
                 base_color=(230, 230, 230),
                 hover_color=(230, 200, 60)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        color = self.hover_color if self.hovered else self.base_color
        label = self.font.render(self.text, True, color)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def is_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )