import pygame, pytmx
from world.collision import *
from world.tilemap import *



class Level:

    def __init__(self, filename):
        self.tilemap = TileMap(filename)
        self.collision = CollisionMap(self.tilemap.tmx)

    def get_spawn(self, name):

        layer = self.tilemap.tmx.get_layer_by_name("Spawn")

        for obj in layer:
            if obj.name == name:
                return pygame.Vector2(obj.x, obj.y)

        raise ValueError(f"No existe un Spawn llamado '{name}'")

    def spawn_player(self, player):
        player.position = self.get_spawn("Player")