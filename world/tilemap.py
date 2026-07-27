import pytmx, pygame


class TileMap:

    def __init__(self, filename):
        self.tmx = pytmx.load_pygame(filename)

    def draw(self, screen, camera):

        for layer in self.tmx.visible_layers:

            if isinstance(layer, pytmx.TiledTileLayer):

                for x, y, gid in layer:

                    tile = self.tmx.get_tile_image_by_gid(gid)
                    if tile:

                        tile_pos = camera.world_to_screen(
                            pygame.Vector2(
                                x * self.tmx.tilewidth,
                                y * self.tmx.tileheight
                            )
                        )

                        screen.blit(tile, tile_pos)