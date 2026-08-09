import pygame


class ShockwaveEffect:
    """Efecto de area en 3 etapas que van creciendo, tipo onda de choque
    (terremoto). Cada etapa dura 'stage_duration' segundos, aplica daño UNA
    sola vez a cada enemigo que agarre (no repite daño si el enemigo sigue
    dentro cuando crece a la siguiente etapa), y se dibuja como un anillo
    que se expande desde el radio anterior hasta el de la etapa actual."""

    def __init__(self, position, stage_radii=(50, 110, 190),
                 stage_duration=0.15, damage_per_stage=15,
                 color=(180, 60, 20)):
        self.position = pygame.Vector2(position)
        self.stage_radii = stage_radii
        self.stage_duration = stage_duration
        self.damage_per_stage = damage_per_stage
        self.color = color

        self.current_stage = 0
        self.stage_timer = 0.0
        self.hit_targets = set()
        self._stages_applied = set()
        self.finished = False

    def update(self, dt, enemies=None):
        if self.finished:
            return

        if self.current_stage not in self._stages_applied:
            self._apply_stage_damage(enemies)
            self._stages_applied.add(self.current_stage)

        self.stage_timer += dt
        if self.stage_timer >= self.stage_duration:
            self.stage_timer = 0.0
            self.current_stage += 1
            if self.current_stage >= len(self.stage_radii):
                self.finished = True

    def _apply_stage_damage(self, enemies):
        if not enemies:
            return

        radius = self.stage_radii[self.current_stage]
        for enemy in enemies:
            if enemy in self.hit_targets:
                continue
            if self.position.distance_to(enemy.position) <= radius:
                enemy.take_damage(self.damage_per_stage)
                self.hit_targets.add(enemy)

    def draw(self, screen, camera):
        if self.finished or self.current_stage >= len(self.stage_radii):
            return

        prev_radius = self.stage_radii[self.current_stage - 1] if self.current_stage > 0 else 0
        target_radius = self.stage_radii[self.current_stage]
        progress = min(self.stage_timer / self.stage_duration, 1.0)
        radius = prev_radius + (target_radius - prev_radius) * progress

        screen_pos = self.position - camera.position
        if radius > 0:
            pygame.draw.circle(screen, self.color, screen_pos, int(radius), width=5)
