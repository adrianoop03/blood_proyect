import pygame


def has_line_of_sight(start, end, collision_rects, step_size=10):
    direction = end - start
    distance = direction.length()
    if distance == 0:
        return True
    direction = direction.normalize()

    steps = int(distance // step_size)
    point = pygame.Vector2(start)

    for _ in range(steps):
        point += direction * step_size
        check_rect = pygame.Rect(point.x - 2, point.y - 2, 4, 4)
        if check_rect.collidelist(collision_rects) != -1:
            return False
    return True


def move_towards(position, rect, target, speed, dt, collision_rects):
    direction = target - position
    if direction.length_squared() > 0:
        direction = direction.normalize()

    new_position = position + direction * speed * dt
    new_rect = rect.copy()
    new_rect.center = new_position

    if new_rect.collidelist(collision_rects) == -1:
        return new_position
    return position
