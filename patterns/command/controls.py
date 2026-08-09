import pygame


class Controls:

    def __init__(self):
        self._prev_keys = {
            "healing": False,
            "attack": False,
            "parry": False,
            "dodge": False,
        }

    def get_direction(self):
        keys = pygame.key.get_pressed()

        movement = pygame.Vector2()

        if keys[pygame.K_a]:
            movement.x -= 1
        if keys[pygame.K_d]:
            movement.x += 1
        if keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_s]:
            movement.y += 1
        if movement.length_squared() > 0:
            movement = movement.normalize()
        return movement

    def get_mouse_position(self):
        return pygame.mouse.get_pos()

    def is_running(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_LSHIFT]

    # --- helper generico de edge-detection (True solo en el frame del flanco) ---
    def _just_pressed(self, name, current):
        was = self._prev_keys[name]
        self._prev_keys[name] = current
        return current and not was

    # --- curar: tecla E ---
    def is_healing(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_e]

    def is_healing_just_pressed(self):
        return self._just_pressed("healing", self.is_healing())

    # --- golpe cuerpo a cuerpo: click izquierdo ---
    def is_attacking(self):
        return pygame.mouse.get_pressed()[0]

    def is_attack_just_pressed(self):
        return self._just_pressed("attack", self.is_attacking())

    # --- disparo: click derecho ---
    def is_parrying(self):
        return pygame.mouse.get_pressed()[2]

    def is_parry_just_pressed(self):
        return self._just_pressed("parry", self.is_parrying())

    # --- esquivar: barra espaciadora ---
    def is_dodging(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_SPACE]

    def is_dodge_just_pressed(self):
        return self._just_pressed("dodge", self.is_dodging())
    def is_getting_damaged(self):
        keys = pygame.key.get_pressed()
        return self._just_pressed("dodge", self.is_dodging())