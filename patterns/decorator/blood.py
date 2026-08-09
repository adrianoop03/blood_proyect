import pygame
import random
import math
import os


class BloodDecals:
    """Maneja las manchas de sangre en el mapa. Es una unica superficie
    persistente del tamaño del nivel: se pinta una vez por evento (no cada
    frame) y despues solo se recorta y dibuja la parte visible.

    Los splats se organizan por 'tipo' de sangre (ej: player, enemy), en
    subcarpetas dentro de splat_root:
        assets/images/blood/player/*.png
        assets/images/blood/enemy/*.png
    Si no hay subcarpetas, todos los .png sueltos en splat_root se cargan
    como el tipo "default"."""

    def __init__(self, level_size, splat_root="assets/images/blood"):
        self.world_surface = pygame.Surface(level_size, pygame.SRCALPHA)
        self.splats_by_type = self._load_splat_types(splat_root)

    def _load_splats(self, folder):
        images = []
        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith(".png"):
                images.append(
                    pygame.image.load(os.path.join(folder, filename)).convert_alpha()
                )
        if not images:
            raise ValueError(f"No se encontraron sprites de sangre en {folder}")
        return images

    def _load_splat_types(self, root):
        types = {}
        for entry in os.listdir(root):
            full_path = os.path.join(root, entry)
            if os.path.isdir(full_path):
                types[entry] = self._load_splats(full_path)

        if not types:
            types["default"] = self._load_splats(root)

        return types

    def get_splats(self, blood_type):
        return self.splats_by_type.get(blood_type, self.splats_by_type.get("default", []))

    def splash_world(self, world_position, blood_type="default", count=1,
                      min_scale=0.9, max_scale=1.4, spread=140, avoid_rect=None):
        """Tira una (o pocas) mancha 'ya armada' cerca de world_position.
        count=1 por defecto: una sola mancha grande se ve mejor que varias
        chicas amontonadas. avoid_rect (ej: player.hitbox) evita que la
        mancha caiga justo debajo del sprite que la genero: el offset se
        samplea con un radio MINIMO que ya saca el centro de la mancha mas
        alla del avoid_rect, en vez de samplear a ciegas y reintentar."""

        splats = self.get_splats(blood_type)
        if not splats:
            return

        min_offset = 0
        if avoid_rect is not None:
            # la mitad de la diagonal del avoid_rect + margen, para que el
            # offset minimo ya empiece afuera de el
            min_offset = max(avoid_rect.width, avoid_rect.height) / 2 + 20

        max_offset = max(spread, min_offset + 1)

        for _ in range(count):
            splat = random.choice(splats)
            scale = random.uniform(min_scale, max_scale)
            angle = random.uniform(0, 360)
            transformed = pygame.transform.rotozoom(splat, angle, scale)

            for attempt in range(6):
                direction = random.uniform(0, 2 * math.pi)
                distance = random.uniform(min_offset, max_offset)
                offset = pygame.Vector2(
                    math.cos(direction),
                    math.sin(direction)
                ) * distance

                pos = world_position + offset
                rect = transformed.get_rect(center=pos)

                if avoid_rect is None or not rect.colliderect(avoid_rect):
                    self.world_surface.blit(transformed, rect)
                    break
                # si choca con avoid_rect, reintenta con otro offset
                # (hasta 4 intentos); si ninguno funciona, se descarta

    def draw(self, screen, camera):
        """Dibujar SOLO la parte visible de la capa de sangre. Llamar entre
        el dibujado del piso/tilemap y el de las entidades."""
        visible_rect = pygame.Rect(
            camera.position.x,
            camera.position.y,
            screen.get_width(),
            screen.get_height()
        )
        screen.blit(self.world_surface, (0, 0), area=visible_rect)
