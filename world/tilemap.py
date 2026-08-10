import pytmx, pygame


class TileMap:

    def __init__(self, filename):
        self.tmx = pytmx.load_pygame(filename)

    def draw(self, screen, camera):

        tile_w = self.tmx.tilewidth
        tile_h = self.tmx.tileheight
        margin = 2

        cam_left = camera.position.x
        cam_top = camera.position.y
        cam_right = camera.position.x + camera.width
        cam_bottom = camera.position.y + camera.height

        x0 = max(0, int(cam_left // tile_w) - margin)
        y0 = max(0, int(cam_top // tile_h) - margin)

        x1 = min(
            self.tmx.width,
            int(cam_right // tile_w) + margin + 1
        )

        y1 = min(
            self.tmx.height,
            int(cam_bottom // tile_h) + margin + 1
        )

        for layer in self.tmx.visible_layers:

            # =========================
            # CAPAS DE TILES
            # =========================

            if isinstance(layer, pytmx.TiledTileLayer):

                for x, y, gid in layer:

                    # Solo dibujar tiles dentro de la cámara
                    if not (x0 <= x < x1 and y0 <= y < y1):
                        continue

                    tile = self.tmx.get_tile_image_by_gid(gid)

                    if tile:

                        tile_pos = camera.world_to_screen(
                            pygame.Vector2(
                                x * tile_w,
                                y * tile_h
                            )
                        )

                        screen.blit(tile, tile_pos)

            # =========================
            # CAPAS DE OBJETOS
            # =========================

            elif isinstance(layer, pytmx.TiledObjectGroup):

                for obj in layer:

                    if not obj.image:
                        continue

                    # No cargar objetos fuera de la cámara
                    if (
                        obj.x + obj.width < cam_left
                        or obj.x > cam_right
                        or obj.y + obj.height < cam_top
                        or obj.y > cam_bottom
                    ):
                        continue

                    obj_pos = camera.world_to_screen(
                        pygame.Vector2(obj.x, obj.y)
                    )

                    screen.blit(obj.image, obj_pos)