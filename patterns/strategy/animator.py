import pygame
import os

class Animator:

    def __init__(self, path, animation_name):
        self.animations = {}
        self.current_animation = animation_name
        ANIMATIONS = {
            "frontwalk": {
                "frames": 11,
                "speed": 0.075
            },
            "backwalk": {
                "frames": 13,
                "speed": 0.075
            },
            "idleAr": {
                "frames": 6,
                "speed": 0.350
            }
        }
        for animation, config in ANIMATIONS.items():
            self.load_animation(
                animation,
                path,
                config["frames"]
            )
        self.animation_config = ANIMATIONS
        self.current_frame = 0
        self.timer = 0


    def load_animation(self, animation_name, path, frame_count):
        if animation_name == "idleAr":
            self.animations[animation_name] = {
                "body": [],
                "head": []
            }
        else:
            self.animations[animation_name] = {
                "feet": [],
                "body": [],
                "head": []
            }
        

        for i in range(frame_count):
            if "feet" in self.animations[animation_name]:
                self.animations[animation_name]["feet"].append(
                    pygame.image.load(
                        os.path.join(path, animation_name, f"{animation_name}_{i:04}_feet.png")
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
            

    def play(self, animation):
        if animation  != self.current_animation:
            self.current_animation = animation
            self.current_frame = 0
            self.timer = 0
        self.speed = self.animation_config[animation]["speed"]
    def update(self, dt):



        self.timer += dt

        if self.timer >= self.speed:

            self.timer = 0

            frames = self.animations[self.current_animation]["body"]

            self.current_frame = (
                self.current_frame + 1
            ) % len(frames)

            
        print(f"Current Animation: {self.current_animation}, Current Frame: {self.current_frame}")
    @property
    def feet(self):
        if "feet" in self.animations[self.current_animation]:
            return self.animations[self.current_animation]["feet"][self.current_frame]
        return None
    @property
    def torso(self):
        return self.animations[self.current_animation]["body"][self.current_frame]
    @property
    def head(self):
        return self.animations[self.current_animation]["head"][self.current_frame]