import pygame, pytmx, random
from world.collision import *

from world.tilemap import *
from world.collisionmap import CollisionMap


class Level:

    # radio maximo (en tiles) que se explora alrededor del jugador para
    # buscar puntos de spawn. No hace falta recorrer el mapa entero: con
    # esto alcanza y sobra para que los enemigos aparezcan cerca de la
    # camara, y en mapas gigantes evita el freeze de varios segundos.
    REACHABLE_SEARCH_RADIUS_TILES = 100

    def __init__(self, filename):
        self.tilemap = TileMap(filename)
        self.collisionmap = CollisionMap(self.tilemap.tmx)
        self.collision = self.collisionmap  # alias, evita parsear la capa dos veces
        self.map_width = self.tilemap.tmx.width * self.tilemap.tmx.tilewidth
        self.map_height = self.tilemap.tmx.height * self.tilemap.tmx.tileheight
        self._reachable_tiles = None
        self._reachable_origin = None

    @property
    def width(self):
        tmx = self.tilemap.tmx
        return tmx.width * tmx.tilewidth

    @property
    def height(self):
        tmx = self.tilemap.tmx
        return tmx.height * tmx.tileheight

    def get_spawn(self, name):
        layer = self.tilemap.tmx.get_layer_by_name("Spawn")

        for obj in layer:
            if obj.name == name:
                return pygame.Vector2(obj.x, obj.y)

        raise ValueError(f"No existe un Spawn llamado '{name}'")

    def spawn_player(self, player):
        player.position = self.get_spawn("Player")

    def get_reachable_tiles(self, start_position):
        tile_w = self.tilemap.tmx.tilewidth
        tile_h = self.tilemap.tmx.tileheight

        start_gx = int(start_position.x // tile_w)
        start_gy = int(start_position.y // tile_h)

        # Si ya calculamos el area alrededor de este mismo origen, reusarla.
        if self._reachable_tiles is not None and self._reachable_origin == (start_gx, start_gy):
            return self._reachable_tiles

        radius = self.REACHABLE_SEARCH_RADIUS_TILES
        min_gx = max(0, start_gx - radius)
        max_gx = min(self.tilemap.tmx.width - 1, start_gx + radius)
        min_gy = max(0, start_gy - radius)
        max_gy = min(self.tilemap.tmx.height - 1, start_gy + radius)

        # Solo miramos que gid exista dentro de esa ventana acotada,
        # en vez de barrer el mapa entero como antes.
        solid_tiles = set()
        for layer in self.tilemap.tmx.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for gy in range(min_gy, max_gy + 1):
                    row = layer.data[gy]
                    for gx in range(min_gx, max_gx + 1):
                        if row[gx]:
                            solid_tiles.add((gx, gy))

        def is_blocked(gx, gy):
            px = gx * tile_w + tile_w / 2
            py = gy * tile_h + tile_h / 2
            rect = pygame.Rect(
                px - tile_w * 0.4, py - tile_h * 0.4,
                tile_w * 0.8, tile_h * 0.8
            )
            return rect.collidelist(self.collision.rects) != -1

        visited = set()
        stack = [(start_gx, start_gy)]
        visited.add((start_gx, start_gy))

        while stack:
            gx, gy = stack.pop()
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = gx + dx, gy + dy
                if (nx, ny) in visited:
                    continue
                if not (min_gx <= nx <= max_gx and min_gy <= ny <= max_gy):
                    continue
                if (nx, ny) not in solid_tiles:
                    continue
                if is_blocked(nx, ny):
                    continue
                visited.add((nx, ny))
                stack.append((nx, ny))

        reachable = []
        for gx, gy in visited:
            px = gx * tile_w + tile_w / 2
            py = gy * tile_h + tile_h / 2
            reachable.append((px, py))

        self._reachable_tiles = reachable
        self._reachable_origin = (start_gx, start_gy)
        return reachable

    def generate_enemy_spawns(self, count, player_position, min_distance_from_player=400, enemy_size=32, max_attempts=2000):
        walkable = self.get_reachable_tiles(player_position)
        spawns = []
        attempts = 0

        while len(spawns) < count and attempts < max_attempts:
            attempts += 1

            x, y = random.choice(walkable)

            if pygame.Vector2(x, y).distance_to(player_position) < min_distance_from_player:
                continue

            check_rect = pygame.Rect(
                x - enemy_size / 2,
                y - enemy_size / 2,
                enemy_size,
                enemy_size
            )

            if check_rect.collidelist(self.collision.rects) != -1:
                continue

            too_close_to_other_spawn = False
            for existing in spawns:
                if pygame.Vector2(x, y).distance_to(existing) < 200:
                    too_close_to_other_spawn = True
                    break

            if too_close_to_other_spawn:
                continue

            spawns.append(pygame.Vector2(x, y))

        return spawns