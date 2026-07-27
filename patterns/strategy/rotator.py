class Rotator:

    def rotate(self, current, target, speed, dt):

        difference = (target - current + 180) % 360 - 180

        max_rotation = speed * dt
        if abs(difference) <= max_rotation:
            return target
        if abs(difference) > 90:
            return target

        return current + (
            max_rotation if difference > 0 else -max_rotation
        )
        


    def update(self, player, dt):

        player.move_angle = self.rotate(
            player.move_angle,
            player.move_target_angle,
            player.rotation_speed,
            dt
        )

        player.aim_angle = self.rotate(
            player.aim_angle,
            player.aim_target_angle,
            player.rotation_speed,
            dt
        )
        
        player.torso_angle = self.rotate(
            player.aim_angle,
            player.aim_target_angle,
            player.rotation_speed,
            dt
        )
        