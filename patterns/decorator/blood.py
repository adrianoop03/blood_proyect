import pygame
import random
import os


class BloodDecals:
    """Maneja las manchas de sangre en el mapa. Es una unica superficie
    persistente del tamaño del nivel: se pinta una vez por evento (no cada
    frame) y despues solo se recorta y dibuja la parte visible."""

    def __init__(self, level_size, splat_folder="assets/images/blood"):
        self.world_surface = pygame.Surface(level_size, pygame.SRCALPHA)
        self.splat_images = self._load_splats(splat_folder)

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

    def splash_world(self, world_position, count=6, min_scale=0.5, max_scale=1.3, spread=40):
        """Tira varias manchas alrededor de una posicion del mundo (ej: donde
        murio un enemigo, o donde el jugador recibio un golpe)."""
        for _ in range(count):
            splat = random.choice(self.splat_images)

            scale = random.uniform(min_scale, max_scale)
            angle = random.uniform(0, 360)
            splat = pygame.transform.rotozoom(splat, angle, scale)

            offset = pygame.Vector2(
                random.uniform(-spread, spread),
                random.uniform(-spread, spread)
            )
            pos = world_position + offset

            rect = splat.get_rect(center=pos)
            self.world_surface.blit(splat, rect)

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


class BloodStainable:
    """Mixin para que una entidad (Player, Enemy, etc.) pueda acumular
    manchas propias que se mueven y rotan junto con su sprite."""

    def init_blood_layer(self, size):
        # 'size' deberia ser un poco mas grande que el sprite del cuerpo
        # para que las manchas no se corten en los bordes al rotar
        self.blood_layer = pygame.Surface(size, pygame.SRCALPHA)

    def add_local_stain(self, splat_images, count=1, min_scale=0.25, max_scale=0.6):
        if not hasattr(self, "blood_layer"):
            return

        w, h = self.blood_layer.get_size()

        for _ in range(count):
            splat = random.choice(splat_images)
            splat = pygame.transform.rotozoom(
                splat,
                random.uniform(0, 360),
                random.uniform(min_scale, max_scale)
            )
            pos = (
                random.randint(0, w),
                random.randint(0, h)
            )
            rect = splat.get_rect(center=pos)
            self.blood_layer.blit(splat, rect)

    def draw_blood_layer(self, screen, camera, angle):
        """Llamar en el draw() de la entidad, despues de dibujar el body
        (para que la sangre quede encima de la piel/ropa)."""
        if not hasattr(self, "blood_layer"):
            return

        stained = pygame.transform.rotate(self.blood_layer, -angle)
        stained_rect = stained.get_rect(center=self.position - camera.position)
        screen.blit(stained, stained_rect)
