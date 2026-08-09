import pygame
import os

from patterns.strategy.animationPlayer import AnimationPlayer

class Animator:

    def __init__(self, path, animation_name):
        self.animations = {}
        self.current_animation = animation_name
        ANIMATIONS = {
            "healing": {
                "frames": 19,
                "speed": 0.1,
                "has_legs": False,
                "loop": False
            },
            "frontwalk": {
                "frames": 11,
                "speed": 0.075,
                "has_legs": True,
                "loop": True
            },
            "backwalk": {
                "frames": 13,
                "speed": 0.075,
                "has_legs": True,
                "loop": True
            },
            "idleAr": {
                "frames": 7,
                "speed": 0.350,
                "has_legs": True,
                "loop": True
            }
        }
        for animation, config in ANIMATIONS.items():
            self.load_animation(
                animation,
                path,
                config["frames"],
                config["has_legs"]
            )
        self.animation_config = ANIMATIONS
        self.current_frame = 0
        self.timer = 0
        self.legs_player = AnimationPlayer()
        self.body_player = AnimationPlayer()
        self.head_player = AnimationPlayer()

        # arrancar con una animacion valida desde el primer frame, para que
        # torso/head/legs nunca devuelvan self.animations[None]
        self.play_body(animation_name)
        self.play_head(animation_name)
        if ANIMATIONS[animation_name]["has_legs"]:
            self.play_legs(animation_name)


    def load_animation(self, animation_name, path, frame_count, has_legs):
        if not has_legs:
            self.animations[animation_name] = {
                "body": [],
                "head": []
            }
        else:
            self.animations[animation_name] = {
                "legs": [],
                "body": [],
                "head": []
            }
        

        for i in range(frame_count):
            if "legs" in self.animations[animation_name]:
                self.animations[animation_name]["legs"].append(
                    pygame.image.load(
                        os.path.join(path, animation_name, f"{animation_name}_{i:04}_legs.png")
                    ).convert_alpha()
                )

            self.animations[animation_name]["body"].append(
                pygame.image.load(
                    os.path.join(path, animation_name, f"{animation_name}_{i:04}_body.png")
                ).convert_alpha()
            )

            self.animations[animation_name]["head"].append(
                pygame.image.load(
                    os.path.join(path, animation_name, f"{animation_name}_{i:04}_head.png")
                ).convert_alpha()
            )
        for name, anim in self.animations.items():
            print(name)

            if "legs" in anim:
                print("legs:", len(anim["legs"]))

            print("body:", len(anim["body"]))
            print("head:", len(anim["head"]))

    def play_legs(self, animation):
        self.legs_player.play(
            animation,
            self.animation_config[animation]["speed"],
            self.animation_config[animation]["loop"]
        )

    def play_body(self, animation):
        self.body_player.play(
            animation,
            self.animation_config[animation]["speed"],
            self.animation_config[animation]["loop"]
        )

    def play_head(self, animation):
        self.head_player.play(
            animation,
            self.animation_config[animation]["speed"],
            self.animation_config[animation]["loop"]
        )
    def update(self, dt):
        
        if self.legs_player.animation is not None:
            self.legs_player.update(
                dt,
                len(self.animations[self.legs_player.animation]["legs"])
            )

        self.body_player.update(
            dt,
            len(
                self.animations[self.body_player.animation]["body"]
            )
        )

        self.head_player.update(
            dt,
            len(
                self.animations[self.head_player.animation]["head"]
            )
        )
            
    @property
    def legs(self):
        if self.legs_player.animation is None:
            return None

        animation = self.animations[self.legs_player.animation]

        if "legs" not in animation:
            return None

        return animation["legs"][self.legs_player.frame]
    
    @property
    def torso(self):
        animation = self.animations[self.body_player.animation]
        return animation["body"][self.body_player.frame]
    
    @property
    def head(self):
        animation = self.animations[self.head_player.animation]
        return animation["head"][self.head_player.frame]
