
class AnimationPlayer:

    def __init__(self):
        self.animation = None
        self.frame = 0
        self.timer = 0
        self.speed = 0
        self.finished = False
        self.loop = True

    def play(self, animation, speed, loop=True):
        if animation != self.animation:
            self.animation = animation
            self.frame = 0
            self.timer = 0
            self.speed = speed
            self.finished = False
            self.loop = loop

    def update(self, dt, frame_count):
        self.timer += dt

        if self.timer >= self.speed:
            self.timer -= self.speed
            self.frame += 1

            if self.frame >= frame_count:
                if self.loop:
                    self.frame = 0
                else:
                    self.frame = frame_count - 1
                    self.finished = True