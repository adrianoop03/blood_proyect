import math
import pygame


class PlayerState:
    """Estado base. Cada estado concreto sobreescribe lo que necesite."""

    def enter(self, player):
        pass

    def update(self, player, dt, walls, enemies=None):
        """Lógica del estado (animaciones, movimiento, fin de animación, etc).
        Devolver una instancia de estado para transicionar, o None para quedarse."""
        return None

    def handle_input(self, player):
        """Chequeo de inputs que pueden interrumpir este estado.
        Devolver una instancia de estado para transicionar, o None."""
        return None

    def exit(self, player):
        pass


# ---------------------------------------------------------------------------
# Estado base: idle / caminar. Es la "puerta de entrada" a todas las acciones.
# ---------------------------------------------------------------------------
class FreeState(PlayerState):

    def handle_input(self, player):
        if player.controls.is_healing_just_pressed():
            return HealingState()
        if player.controls.is_shoot_just_pressed():
            return ShootState()
        if player.controls.is_attack_just_pressed():
            return Attack1State()
        if player.controls.is_dodge_just_pressed() and player.can_dodge():
            return DodgeState()
        return None

    def update(self, player, dt, walls, enemies=None):
        # locomoción completa: mueve, y sincroniza piernas + cuerpo + cabeza
        player.apply_locomotion(dt, walls, sync_body_head=True)
        return None


# ---------------------------------------------------------------------------
# Curación: se puede seguir caminando mientras cura (piernas libres),
# termina sola cuando la animación de body/head llega al final.
# ---------------------------------------------------------------------------
class HealingState(PlayerState):

    def enter(self, player):
        player.animator.play_body("healing")
        player.animator.play_head("healing")

    def update(self, player, dt, walls, enemies=None):
        # solo piernas: body/head deben seguir en "healing", no pisarlos
        player.apply_locomotion(dt, walls, sync_body_head=False)
        if player.animator.body_player.frame == 9:
            player.heal(5)
        if player.animator.body_player.finished:
            return FreeState()
        return None


# ---------------------------------------------------------------------------
# Disparo: una sola fase, 100% bloqueada, sin cancelación ni movimiento.
# ---------------------------------------------------------------------------
class ShootState(PlayerState):

    def enter(self, player):
        player.animator.play_legs("idleAr")
        player.animator.play_body("shoot")
        player.animator.play_head("shoot")
        player.fire_bullets()

    def update(self, player, dt, walls, enemies=None):
        if player.animator.body_player.finished:
            return FreeState()
        return None


# ---------------------------------------------------------------------------
# Golpes: fase activa bloqueada (sin input, sin movimiento) + hitbox activo
# solo durante una ventana de frames dentro de esa fase activa + fase de
# recuperación cancelable (dodge / heal / siguiente golpe del combo). Si la
# recuperación termina sin cancelar, vuelve a Free.
# ---------------------------------------------------------------------------
class MeleeAttackState(PlayerState):
    """Clase base para ataque1/2/3. Cada subclase define animation_name,
    lock_until_frame, ventana de hitbox y a qué estado avanza el combo."""

    animation_name = None       # nombre de la animación en Animator
    lock_until_frame = 0        # frame en el que empieza la recuperación
    next_combo_state = None     # clase del siguiente estado del combo (o None)

    # ventana de frames (dentro de la fase activa) en la que el hitbox
    # existe de verdad — el resto de la fase activa es solo windup/retorno
    hit_frame_start = 3
    hit_frame_end = 6

    hit_reach = 70        # distancia del hitbox desde el centro del jugador
    hit_size = (70, 70)   # ancho, alto del hitbox
    damage = 15

    def __init__(self):
        self.hit_targets = set()

    def enter(self, player):
        player.animator.play_body(self.animation_name)
        player.animator.play_head(self.animation_name)
        self.hit_targets = set()

    def _in_recovery(self, player):
        return player.animator.body_player.frame >= self.lock_until_frame

    def _in_hit_window(self, player):
        frame = player.animator.body_player.frame
        return self.hit_frame_start <= frame <= self.hit_frame_end

    def _get_hitbox(self, player):
        forward = pygame.Vector2(
            math.cos(math.radians(player.aim_angle + 90)),
            math.sin(math.radians(player.aim_angle + 90))
        )
        center = player.position + forward * self.hit_reach
        rect = pygame.Rect(0, 0, *self.hit_size)
        rect.center = center
        return rect

    def _apply_hits(self, player, enemies):
        if not enemies or not self._in_hit_window(player):
            return

        hitbox = self._get_hitbox(player)
        for enemy in enemies:
            if enemy in self.hit_targets:
                continue
            if hitbox.colliderect(enemy.hitbox):
                enemy.take_damage(self.damage)
                self.hit_targets.add(enemy)

    def handle_input(self, player):
        if not self._in_recovery(player):
            return None  # fase activa: controles bloqueados, sin excepciones

        if player.controls.is_dodge_just_pressed() and player.can_dodge():
            return DodgeState()
        if player.controls.is_healing_just_pressed():
            return HealingState()
        if player.controls.is_attack_just_pressed() and self.next_combo_state:
            return self.next_combo_state()
        return None

    def update(self, player, dt, walls, enemies=None):
        self._apply_hits(player, enemies)

        if self._in_recovery(player):
            # recuperación: piernas libres para moverse, body/head siguen
            # con la animación de golpe hasta que termine
            player.apply_locomotion(dt, walls, sync_body_head=False)
        # fase activa: sin locomoción, quieto en el lugar

        if player.animator.body_player.finished:
            return FreeState()
        return None


class Attack1State(MeleeAttackState):
    animation_name = "attack1"
    lock_until_frame = 10
    next_combo_state = None  # se asigna abajo para evitar referencia circular


class Attack2State(MeleeAttackState):
    animation_name = "attack2"
    lock_until_frame = 10
    next_combo_state = None
    damage = 18


class Attack3State(MeleeAttackState):
    animation_name = "attack3"
    lock_until_frame = 10
    next_combo_state = None  # último del combo: no encadena a nada
    damage = 22

    def _apply_hits(self, player, enemies):
        had_hits_before = bool(self.hit_targets)
        super()._apply_hits(player, enemies)

        # dispara el shockwave la primera vez que el 3er golpe conecta
        if not had_hits_before and self.hit_targets:
            player.trigger_shockwave()


# encadenar el combo sin referencias circulares en la definición de clase
Attack1State.next_combo_state = Attack2State
Attack2State.next_combo_state = Attack3State


# ---------------------------------------------------------------------------
# Esquivar: dash rapido + invulnerabilidad durante toda la duracion.
# Direccion: la del movimiento si hay input, si no la opuesta al mouse.
# ---------------------------------------------------------------------------
class DodgeState(PlayerState):

    dash_speed = 1200      # velocidad del dash (ajustar a gusto)
    duration = 0.25        # segundos que dura el dash / la invulnerabilidad

    def __init__(self):
        self.direction = pygame.Vector2(0, -1)
        self.timer = 0

    def enter(self, player):
        move_input = player.controls.get_direction()

        if move_input.length_squared() > 0:
            self.direction = move_input
        else:
            # direccion desde la que el personaje mira al mouse (misma
            # convencion que se usa para frontwalk/backwalk), invertida
            aim_direction = pygame.Vector2(
                math.cos(math.radians(player.aim_angle + 90)),
                math.sin(math.radians(player.aim_angle + 90))
            )
            self.direction = -aim_direction

        self.timer = 0
        player.invulnerable = True
        player.consume_energy(player.dodge_energy_cost)

#        player.animator.play_legs("dodge")
#        player.animator.play_body("dodge")
#        player.animator.play_head("dodge")

    def update(self, player, dt, walls, enemies=None):
        self.timer += dt

        # empuja al jugador en la direccion fijada, con colision, ignorando
        # el input en vivo (a diferencia de apply_locomotion)
        original_speed = player.speed
        player.speed = self.dash_speed
        player.movement.move(player, self.direction, dt, walls)
        player.speed = original_speed

        if self.timer >= self.duration:
            return FreeState()
        return None

    def exit(self, player):
        player.invulnerable = False
