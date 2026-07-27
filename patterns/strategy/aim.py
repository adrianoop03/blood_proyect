import math

class Aim:

    def update(self, player, mouse_world):

        dx = mouse_world.x - player.position.x
        dy = mouse_world.y - player.position.y

        player.aim_target_angle = (
            math.degrees(
                math.atan2(dy, dx)
            ) - 90
        )
    