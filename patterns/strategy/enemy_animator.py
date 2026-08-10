import pygame
import os

from patterns.strategy.animationPlayer import AnimationPlayer


ENEMY_ANIMATIONS = {
    "idle_armed": {
        "folder": "idle armado",
        "prefix": "idle_Arm",
        "frames": 6,
        "speed": 0.2,
        "loop": True
    },
    "walk": {
        "folder": "frontwalk",
        "prefix": "frontwalk",
        "frames": 9,
        "speed": 0.1,
        "loop": True
    },
    "attack1": {
        "folder": os.path.join("attack", "attack 1"),
        "prefix": "attack1",
        "frames": 14,
        "speed": 0.08,
        "loop": False
    },
    "attack2": {
        "folder": os.path.join("attack", "attack 2"),
        "prefix": "attack2",
        "frames": 14,
        "speed": 0.08,
        "loop": False
    },
    "hurt": {
        "folder": "take damage",
        "prefix": "takedamage",
        "frames": 7,
        "speed": 0.08,
        "loop": False
    },
    "die": {
        "folder": "die",
        "prefix": "die",
        "frames": 10,
        "speed": 0.1,
        "loop": False
    },
}


class EnemyAnimator:
    """Animator con capas body/head/legs, igual que el del Player, pero
    con carpeta y prefijo de archivo configurables por animacion (los
    assets del enemigo no tienen naming 100% consistente entre carpetas)."""

    def __init__(self, base_path, start_animation, animations_config=ENEMY_ANIMATIONS):
        self.base_path = base_path
        self.animation_config = animations_config
        self.animations = {}

        for name, config in animations_config.items():
            self.load_animation(name, config)

        self.legs_player = AnimationPlayer()
        self.body_player = AnimationPlayer()
        self.head_player = AnimationPlayer()

        self.play(start_animation)

    def load_animation(self, name, config):
        folder = os.path.join(self.base_path, config["folder"])
        prefix = config["prefix"]

        self.animations[name] = {"body": [], "head": [], "legs": []}

        for i in range(config["frames"]):
            for layer in ("body", "head", "legs"):
                image_path = os.path.join(
                    folder,
                    f"{prefix}_{i:04}_{layer}.png"
                )
                self.animations[name][layer].append(
                    pygame.image.load(image_path).convert_alpha()
                )

    def play_legs(self, animation):
        cfg = self.animation_config[animation]
        self.legs_player.play(animation, cfg["speed"], cfg["loop"])

    def play_body(self, animation):
        cfg = self.animation_config[animation]
        self.body_player.play(animation, cfg["speed"], cfg["loop"])

    def play_head(self, animation):
        cfg = self.animation_config[animation]
        self.head_player.play(animation, cfg["speed"], cfg["loop"])

    def play(self, animation):
        self.play_body(animation)
        self.play_head(animation)
        self.play_legs(animation)

    def update(self, dt):
        self.legs_player.update(
            dt, len(self.animations[self.legs_player.animation]["legs"])
        )
        self.body_player.update(
            dt, len(self.animations[self.body_player.animation]["body"])
        )
        self.head_player.update(
            dt, len(self.animations[self.head_player.animation]["head"])
        )

    @property
    def legs(self):
        anim = self.animations[self.legs_player.animation]
        return anim["legs"][self.legs_player.frame]

    @property
    def torso(self):
        anim = self.animations[self.body_player.animation]
        return anim["body"][self.body_player.frame]

    @property
    def head(self):
        anim = self.animations[self.head_player.animation]
        return anim["head"][self.head_player.frame]

    @property
    def finished(self):
        return self.body_player.finished