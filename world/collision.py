import pytmx as tmx
import pygame

class CollisionMap:

    def __init__(self, tmx):

        self.rects = []

        for obj in tmx.get_layer_by_name("collision"):

            self.rects.append(

                pygame.Rect(
                    obj.x,
                    obj.y,
                    obj.width,
                    obj.height
                )

            )