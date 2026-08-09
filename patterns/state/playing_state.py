import pygame
from patterns.state.state import State
from entities.player import Player
from world.level import Level
from patterns.strategy.camera import Camera


class PlayingState(State):
    """Estado de partida: la logica que antes vivia en main.py."""

    def __init__(self, game):
        super().__init__(game)

        self.camera = Camera(1920, 1080)
        self.player = Player()

        self.level = Level("assets/maps/level1.tmx")
        self.level.spawn_player(self.player)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from patterns.state.menu_state import MenuState
            self.game.state_manager.set_state(MenuState(self.game))

    def update(self, dt):
        self.player.update(
            dt,
            self.camera,
            self.level.collisionmap.rects
        )
        self.camera.update(self.player, dt)

    def draw(self, screen):
        self.level.tilemap.draw(screen, self.camera)
        self.player.draw(screen, self.camera)
