import pygame
import random


class SkillBoard:

    def __init__(self, screen_width, screen_height):
        self.active = False
        self.options = []
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font_title = pygame.font.SysFont("georgia", 46, bold=True)
        self.font_subtitle = pygame.font.SysFont("georgia", 20, italic=True)
        self.font_option_title = pygame.font.SysFont("georgia", 26, bold=True)
        self.font_option_desc = pygame.font.SysFont("georgia", 18)
        self.font_key = pygame.font.SysFont("georgia", 30, bold=True)
        self.font_hint = pygame.font.SysFont("georgia", 18, italic=True)

        self.wood_dark = (46, 30, 20)
        self.wood_mid = (66, 44, 28)
        self.wood_light = (86, 58, 36)
        self.parchment = (222, 199, 156)
        self.parchment_dark = (196, 170, 128)
        self.ink = (46, 32, 20)
        self.nail_color = (70, 70, 74)
        self.rope_color = (120, 96, 60)

        self.card_rotations = []
        self.card_surfaces = []  # superficies de pergamino pre-renderizadas, generadas una sola vez en open()

    def open(self, upgrade_pool, count=3):
        self.options = random.sample(upgrade_pool, min(count, len(upgrade_pool)))
        self.active = True
        self._prepare_cards()

    def handle_key(self, key, player):
        if not self.active:
            return False

        index = None
        if key == pygame.K_1:
            index = 0
        elif key == pygame.K_2:
            index = 1
        elif key == pygame.K_3:
            index = 2

        if index is not None and index < len(self.options):
            self.options[index].apply(player)
            self.active = False
            self.options = []
            return True

        return False

    def _generate_parchment_surface(self, width, height):
        card_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)

        jag = 6
        points = []
        segments_x = 10
        segments_y = 14

        for i in range(segments_x + 1):
            x = 10 + (width * i / segments_x)
            points.append((x, 10 + random.uniform(-jag, jag)))
        for i in range(segments_y + 1):
            y = 10 + (height * i / segments_y)
            points.append((10 + width + random.uniform(-jag, jag), y))
        for i in range(segments_x + 1):
            x = 10 + width - (width * i / segments_x)
            points.append((x, 10 + height + random.uniform(-jag, jag)))
        for i in range(segments_y + 1):
            y = 10 + height - (height * i / segments_y)
            points.append((10 + random.uniform(-jag, jag), y))

        pygame.draw.polygon(card_surface, self.parchment_dark, points)
        inset_points = [(p[0] * 0.97 + width * 0.015, p[1] * 0.97 + height * 0.015) for p in points]
        pygame.draw.polygon(card_surface, self.parchment, inset_points)

        for _ in range(18):
            sx = random.uniform(10, width + 10)
            sy = random.uniform(10, height + 10)
            stain_color = (*self.parchment_dark, 40)
            pygame.draw.circle(card_surface, stain_color, (sx, sy), random.uniform(4, 14))

        return card_surface

    def _prepare_cards(self):
        # calcula las mismas dimensiones que se usan en draw() para las cartas,
        # genera cada superficie de pergamino UNA sola vez y las guarda en cache
        board_width = min(1400, self.screen_width - 160)
        board_height = min(760, self.screen_height - 140)
        board_x = (self.screen_width - board_width) / 2
        board_y = (self.screen_height - board_height) / 2
        board_rect = pygame.Rect(board_x, board_y, board_width, board_height)

        title_y = board_rect.top + 22
        rope_y = title_y + 95

        card_count = len(self.options)
        card_width = min(340, (board_rect.width - 120) / max(card_count, 1))
        card_height = board_rect.height - 220

        self.card_rotations = [random.uniform(-3, 3) for _ in range(card_count)]
        self.card_surfaces = []

        for i in range(card_count):
            surface = self._generate_parchment_surface(card_width, card_height)
            rotated = pygame.transform.rotate(surface, self.card_rotations[i])
            self.card_surfaces.append(rotated)

    def _draw_wood_background(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        board_width = min(1400, self.screen_width - 160)
        board_height = min(760, self.screen_height - 140)
        board_x = (self.screen_width - board_width) / 2
        board_y = (self.screen_height - board_height) / 2

        board_rect = pygame.Rect(board_x, board_y, board_width, board_height)
        pygame.draw.rect(screen, self.wood_dark, board_rect, border_radius=6)

        plank_count = 8
        plank_height = board_height / plank_count
        for i in range(plank_count):
            y = board_y + i * plank_height
            color = self.wood_mid if i % 2 == 0 else self.wood_light
            plank_rect = pygame.Rect(board_x, y, board_width, plank_height)
            pygame.draw.rect(screen, color, plank_rect)
            pygame.draw.line(screen, self.wood_dark, (board_x, y), (board_x + board_width, y), 2)

        pygame.draw.rect(screen, self.wood_dark, board_rect, width=10, border_radius=6)

        for corner in [
            (board_x + 20, board_y + 20),
            (board_x + board_width - 20, board_y + 20),
            (board_x + 20, board_y + board_height - 20),
            (board_x + board_width - 20, board_y + board_height - 20),
        ]:
            pygame.draw.circle(screen, (30, 30, 32), corner, 7)
            pygame.draw.circle(screen, (90, 90, 96), corner, 7, 1)

        return board_rect

    def _draw_nail(self, screen, pos):
        pygame.draw.circle(screen, (20, 20, 22), (pos[0] + 2, pos[1] + 2), 8)
        pygame.draw.circle(screen, self.nail_color, pos, 8)
        pygame.draw.circle(screen, (150, 150, 156), (pos[0] - 2, pos[1] - 2), 3)

    def draw(self, screen):
        if not self.active:
            return

        board_rect = self._draw_wood_background(screen)

        title_text = self.font_title.render("TABLÓN DE CAZA", True, self.parchment)
        title_shadow = self.font_title.render("TABLÓN DE CAZA", True, (0, 0, 0))
        title_x = board_rect.centerx - title_text.get_width() / 2
        title_y = board_rect.top + 22
        screen.blit(title_shadow, (title_x + 3, title_y + 3))
        screen.blit(title_text, (title_x, title_y))

        subtitle_text = self.font_subtitle.render("Elegí una recompensa por tu caza", True, (200, 180, 150))
        screen.blit(subtitle_text, (board_rect.centerx - subtitle_text.get_width() / 2, title_y + 60))

        rope_y = title_y + 95
        pygame.draw.line(screen, self.rope_color, (board_rect.left + 40, rope_y), (board_rect.right - 40, rope_y), 3)

        card_count = len(self.options)
        card_width = min(340, (board_rect.width - 120) / max(card_count, 1))
        card_height = board_rect.height - 220
        spacing = 30
        total_width = card_width * card_count + spacing * (card_count - 1)
        start_x = board_rect.centerx - total_width / 2
        card_y = rope_y + 40

        keys = ["1", "2", "3"]

        for i, upgrade in enumerate(self.options):
            card_x = start_x + i * (card_width + spacing)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

            # usa la superficie ya generada en open(), no la vuelve a calcular cada frame
            card_surface = self.card_surfaces[i]
            rotated_rect = card_surface.get_rect(center=card_rect.center)
            screen.blit(card_surface, rotated_rect)

            self._draw_nail(screen, (rotated_rect.centerx, rotated_rect.top + 14))

            content_rect = card_rect.inflate(-40, -40)

            key_badge_center = (content_rect.centerx, content_rect.top + 10)
            pygame.draw.circle(screen, self.wood_dark, key_badge_center, 22)
            pygame.draw.circle(screen, self.parchment, key_badge_center, 22, 2)
            key_text = self.font_key.render(keys[i], True, self.ink)
            screen.blit(key_text, (key_badge_center[0] - key_text.get_width() / 2, key_badge_center[1] - key_text.get_height() / 2))

            name_lines = self._wrap_text(upgrade.name, self.font_option_title, content_rect.width)
            text_y = content_rect.top + 50
            for line in name_lines:
                line_surf = self.font_option_title.render(line, True, self.ink)
                screen.blit(line_surf, (content_rect.centerx - line_surf.get_width() / 2, text_y))
                text_y += line_surf.get_height() + 2

            pygame.draw.line(
                screen, self.parchment_dark,
                (content_rect.left + 20, text_y + 8),
                (content_rect.right - 20, text_y + 8),
                1
            )
            text_y += 20

            desc_lines = self._wrap_text(upgrade.description, self.font_option_desc, content_rect.width - 10)
            for line in desc_lines:
                line_surf = self.font_option_desc.render(line, True, (70, 50, 30))
                screen.blit(line_surf, (content_rect.centerx - line_surf.get_width() / 2, text_y))
                text_y += line_surf.get_height() + 4

        hint_text = self.font_hint.render("Presioná 1, 2 o 3 para elegir", True, (200, 180, 150))
        screen.blit(hint_text, (board_rect.centerx - hint_text.get_width() / 2, board_rect.bottom - 40))

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
