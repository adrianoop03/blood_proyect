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
        if player.controls.is_parry_just_pressed():
            return ParryState()
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

    sound_frame = 9  # frame de la animacion en el que suena el heal
    heal_frame = 9   # frame en el que se aplica la curacion real
    heal_amount = 20

    def enter(self, player):
        player.animator.play_body("healing")
        player.animator.play_head("healing")
        self._sound_played = False
        self._heal_applied = False

    def update(self, player, dt, walls, enemies=None):
        # solo piernas: body/head deben seguir en "healing", no pisarlos
        player.apply_locomotion(dt, walls, sync_body_head=False)

        frame = player.animator.body_player.frame
                           

        if not self._heal_applied and frame >= self.heal_frame:
            self._heal_applied = True
            player.heal(self.heal_amount)

        if not self._sound_played and frame >= self.sound_frame:
            self._sound_played = True
            if player.sound_manager:
                player.sound_manager.play("heal")

        if player.animator.body_player.finished:
            return FreeState()
        return None


# ---------------------------------------------------------------------------
# Disparo: una sola fase, 100% bloqueada, sin cancelación ni movimiento.
# ---------------------------------------------------------------------------
class ParryState(PlayerState):

    def enter(self, player):
        player.animator.play_legs("idleAr")
        player.animator.play_body("parry")
        player.animator.play_head("parry")
        player.animation_parry = False
        player.parry_cooldown = False
        

    def update(self, player, dt, walls, enemies=None):
        if not player.animation_parry and player.sound_manager and player.animator.body_player.frame == 5:
            player.sound_manager.play("parry")
            player.animation_parry = True
        if not player.parry_cooldown and player.animator.body_player.frame == 4:
            player.fire_bullets()
            player.parry_cooldown = True
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
    la ventana de hitbox y el frame en el que empieza la recuperacion —
    TODOS estos valores deben caer dentro del rango de frames real de esa
    animacion (0 a frames-1), si no el combo se traba (ver Attack2State)."""
 
    animation_name = None       # nombre de la animación en Animator
    lock_until_frame = 0        # frame en el que empieza la recuperación
    next_combo_state = None     # clase del siguiente estado del combo (o None)
 
    hit_frame_start = 3
    hit_frame_end = 6
 
    hit_reach = 70        # distancia del hitbox desde el centro del jugador
    hit_size = (70, 70)   # ancho, alto del hitbox
    damage = 15
 
    dash_speed = 900       # velocidad del dash de windup
 
    def __init__(self):
        self.hit_targets = set()
 
    def enter(self, player):
        player.animator.play_legs(self.animation_name)
        player.animator.play_body(self.animation_name)
        player.animator.play_head(self.animation_name)
        self.hit_targets = set()
        if player.sound_manager:
            player.sound_manager.play(self.animation_name)  # swing: attack1/2/3
 
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
        new_hits = False
        for enemy in enemies:
            if enemy in self.hit_targets:
                continue
            if hitbox.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                self.hit_targets.add(enemy)
                new_hits = True
 
        if new_hits and player.sound_manager:
            player.sound_manager.play("hit")
 
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
 
        frame = player.animator.body_player.frame
        if frame >= self.hit_frame_start and frame <= self.hit_frame_end:
            # windup: pequeño dash en la direccion del ataque, con colision,
            # en vez de dejar caminar libre
            forward = pygame.Vector2(
                math.cos(math.radians(player.aim_angle + 90)),
                math.sin(math.radians(player.aim_angle + 90))
            )
            original_speed = player.speed
            player.speed = self.dash_speed
            player.movement.move(player, forward, dt, walls)
            player.speed = original_speed
        # durante la ventana de hit y la recuperacion: quieto en el lugar,
        # sin locomocion libre
 
        if player.animator.body_player.finished:
            return FreeState()
        return None


class Attack1State(MeleeAttackState):
    animation_name = "attack1"
    hit_frame_start = 4
    hit_frame_end = 5
    lock_until_frame = 5
    next_combo_state = None  # se asigna abajo para evitar referencia circular
    damage = 18


class Attack2State(MeleeAttackState):
    animation_name = "attack2"
    hit_frame_start = 3
    hit_frame_end = 4
    lock_until_frame = 4
    next_combo_state = None
    damage = 18


class Attack3State(MeleeAttackState):
    animation_name = "attack3"
    hit_frame_start = 5
    hit_frame_end = 6
    lock_until_frame = 7
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

    dash_speed = 1000      # velocidad del dash (ajustar a gusto)
    duration = 0.35        # segundos que dura el dash / la invulnerabilidad

    def __init__(self):
        self.direction = pygame.Vector2(0, -1)
        self.timer = 0

    def enter(self, player):
        move_input = player.controls.get_direction()

        if move_input.length_squared() > 0:
            self.direction = move_input
        else:
                                                                      
                                                                       
            aim_direction = pygame.Vector2(
                math.cos(math.radians(player.aim_angle + 90)),
                math.sin(math.radians(player.aim_angle + 90))
            )
            self.direction = -aim_direction

        # mismo criterio que frontwalk/backwalk: si el dash va "hacia
        # adelante" respecto a hacia donde apunta el mouse, frontdodge;
        # si va "hacia atras", backdodge
        aim_direction = pygame.Vector2(
            math.cos(math.radians(player.aim_angle + 90)),
            math.sin(math.radians(player.aim_angle + 90))
        )
        dot = self.direction.dot(aim_direction)
        self.animation_name = "frontdodge" if dot >= 0 else "backdodge"

        player.animator.play_legs(self.animation_name)
        player.animator.play_body(self.animation_name)
        player.animator.play_head(self.animation_name)

        self.timer = 0
        player.invulnerable = True
        player.consume_energy(player.dodge_energy_cost)

        if player.sound_manager:
            player.sound_manager.play("dodge")

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

# ---------------------------------------------------------------------------
# Muerte: bloquea todo input y movimiento, reproduce la animacion de muerte
# una sola vez y se queda ahi para siempre (estado terminal).
# ---------------------------------------------------------------------------
class DeathState(PlayerState):

    def enter(self, player):
        player.animator.play_body("die")
        player.animator.play_head("die")
        player.invulnerable = True
        if player.sound_manager:
            player.sound_manager.play("die")

    def handle_input(self, player):
        return None  

    def update(self, player, dt, walls, enemies=None):
        return None  
