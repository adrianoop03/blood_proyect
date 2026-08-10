import pygame
import math
import random

from entities.bullet import bullet
from patterns.command.controls import Controls
from patterns.strategy.movement import Movement
from patterns.strategy.aim import Aim
from patterns.strategy.animator import Animator
from patterns.strategy.rotator import Rotator
from patterns.state.states import FreeState , DeathState
from patterns.strategy.effects import ShockwaveEffect


class Player:
    def __init__(self):
        self.bullets = pygame.sprite.Group()
        self.parry_cooldown = 0
        self.parry_delay = 0.3
        self.num_pellets = 5
        self.spread_angle = 10

        self.controls = Controls()
        self.movement = Movement()
        self.aim = Aim()
        self.rotator = Rotator()

        self.animator = Animator(
            "assets/images/player",
            "idleAr"
        )

        self.move_angle = -90
        self.move_target_angle = -90
        self.aim_angle = -90
        self.aim_target_angle = -90
        self.move_direction = pygame.Vector2(0, -1)
        self.target_angle = -90
        self.rotation_speed = 1080  # grados por segundo

        # vida
        self.max_health = 100
        self.health = 100
        self.is_dead = False
        self.flash_timer = 0
        self.flash_duration = 0.15

        # curacion: cargas limitadas, no infinita
        self.max_heal_charges = 3
        self.heal_charges = self.max_heal_charges
        self.heal_amount = 25  # vida que restaura cada carga

        # energia / sprint
        self.max_energy = 100
        self.energy = 100
        self.energy_regen_rate = 20
        self.sprint_energy_cost = 30
        self.base_speed = 400
        self.sprint_speed = 700
        self.speed = self.base_speed

        # delay antes de que la energia empiece a regenerar de nuevo
        # despues de haberla gastado (sprint o dodge)
        self.energy_regen_delay = 1.5
        self._energy_regen_timer = 0.0

        # costo de energia del dodge
        self.dodge_energy_cost = 25

        # disparo
        self.bullets = pygame.sprite.Group()
        # hitbox del jugador
        self.position = pygame.Vector2(0, 0)
        self.hitbox = pygame.Rect(0, 0, 80, 80)
        self.hitbox.center = self.position

        # sangre: se asigna desde afuera (main.py) despues de crear el
        # nivel, ej: player.blood_decals = blood_decals
        self.blood_decals = None

        # sonido: se asigna desde afuera (main.py), ej:
        # player.sound_manager = sound_manager
        self.sound_manager = None
        self._last_legs_frame = -1
        self._last_legs_animation = None

        # frames del ciclo de piernas en los que el pie toca el piso
        # (ajustar a los frames reales de tu spritesheet)
        self.footstep_frames = {
            "frontwalk": {2, 7},
            "backwalk": {3, 9},
            "run": {2, 6},
        }

        # invulnerabilidad (activa mientras dura el dodge)
        self.invulnerable = False

        # efectos activos (ej: shockwave del 3er golpe)
        self.active_effects = []

        # maquina de estados
        self.state = FreeState()
        self.state.enter(self)

    def trigger_shockwave(self):
        self.active_effects.append(
            ShockwaveEffect(self.position)
        )

    def take_damage(self, amount):
        if self.invulnerable:
            return

        self.health -= amount
        self.flash_timer = self.flash_duration

        if self.health < 0:
            self.health = 0

        if self.sound_manager:
            self.sound_manager.play("hurt")

        if self.blood_decals:
            self.blood_decals.splash_world(
                self.position,
                blood_type="player",
                avoid_rect=self.hitbox
            )

        if self.health <= 0 and not self.is_dead:
            self.is_dead = True
            self.state.exit(self)
            self.state = DeathState()
            self.state.enter(self)

    def heal(self, amount):
        self.health += amount

        if self.health > self.max_health:
            self.health = self.max_health

    def try_heal(self):
        """Gasta una carga de curacion, si hay disponible y hace falta.
        Devuelve True si curo, False si no pudo (sin cargas o vida llena)."""
        if self.heal_charges <= 0:
            return False

        if self.health >= self.max_health:
            return False

        self.heal_charges -= 1
        self.heal(self.heal_amount)

        if self.sound_manager:
            self.sound_manager.play("heal")

        return True

    def consume_energy(self, amount):
        """Gasta energia y reinicia el delay antes de que vuelva a regenerar."""
        self.energy -= amount

        if self.energy < 0:
            self.energy = 0

        self._energy_regen_timer = self.energy_regen_delay

    def regen_energy(self, dt):
        if self._energy_regen_timer > 0:
            self._energy_regen_timer -= dt
            return

        self.energy += self.energy_regen_rate * dt

        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def can_dodge(self):
        return self.energy >= self.dodge_energy_cost

    def apply_locomotion(self, dt, walls, sync_body_head):
        direction = self.controls.get_direction()

        is_trying_to_run = (
            self.controls.is_running()
            and direction.length_squared() > 0
        )

        if is_trying_to_run and self.energy > 0:
            self.speed = self.sprint_speed
            self.consume_energy(
                self.sprint_energy_cost * dt
            )
            running = True
        else:
            self.speed = self.base_speed
            running = False

        moving = self.movement.move(
            self,
            direction,
            dt,
            walls
        )

        if moving and running:
            # corriendo: todo el cuerpo va en la direccion de movimiento,
            # ignorando hacia donde apunta el mouse
            self.animator.play_legs("run")

            if sync_body_head:
                self.animator.play_body("run")
                self.animator.play_head("run")

        elif moving:
            aim_direction = pygame.Vector2(
                math.cos(
                    math.radians(self.aim_angle + 90)
                ),
                math.sin(
                    math.radians(self.aim_angle + 90)
                )
            )

            dot = self.move_direction.dot(
                aim_direction
            )

            if dot >= 0:
                self.animator.play_legs("frontwalk")

                if sync_body_head:
                    self.animator.play_body("frontwalk")
                    self.animator.play_head("frontwalk")
            else:
                self.animator.play_legs("backwalk")

                if sync_body_head:
                    self.animator.play_body("backwalk")
                    self.animator.play_head("backwalk")

        else:
            self.animator.play_legs("idleAr")

            if sync_body_head:
                self.animator.play_body("idleAr")
                self.animator.play_head("idleAr")

        return moving

    def _update_footsteps(self):
        legs_anim = self.animator.legs_player.animation
        frame = self.animator.legs_player.frame

        # solo evaluar cuando el frame CAMBIA, no en cada tick de update()
        if (
            legs_anim == self._last_legs_animation
            and frame == self._last_legs_frame
        ):
            return

        self._last_legs_animation = legs_anim
        self._last_legs_frame = frame

        step_frames = self.footstep_frames.get(legs_anim)

        if not step_frames or frame not in step_frames:
            return

        if not self.sound_manager:
            return

        is_running = self.speed > self.base_speed
        category = (
            "footsteps_run"
            if is_running
            else "footsteps_walk"
        )

        self.sound_manager.play_footstep(category)

    def fire_bullets(self):
        num_pellets = self.num_pellets
        spread_angle = self.spread_angle

        for i in range(num_pellets):
            offset = random.uniform(
                -spread_angle / 2,
                spread_angle / 2
            )

            angle = self.aim_angle + 90 + offset

            parry_direction = pygame.Vector2(
                math.cos(math.radians(angle)),
                math.sin(math.radians(angle))
            )

            new_bullet = bullet(
                self.position.x + 175 * parry_direction.x,
                self.position.y + 100 * parry_direction.y,
                parry_direction
            )

            self.bullets.add(new_bullet)

    def update(self, dt, camera, walls, enemies=None):
        if not self.is_dead:
            mouse_world = camera.screen_to_world(
                pygame.mouse.get_pos()
            )

            self.aim.update(
                self,
                mouse_world
            )

        next_state = self.state.handle_input(self)

        if next_state is None:
            next_state = self.state.update(
                self,
                dt,
                walls,
                enemies
            )

        if next_state is not None:
            self.state.exit(self)
            self.state = next_state
            self.state.enter(self)

        self.regen_energy(dt)

        self.parry_cooldown -= dt

        if self.parry_cooldown < 0:
            self.parry_cooldown = 0

        self.bullets.update(
            dt,
            walls
        )

        if self.flash_timer > 0:
            self.flash_timer -= dt

        for effect in self.active_effects:
            effect.update(
                dt,
                enemies
            )

        self.active_effects = [
            e
            for e in self.active_effects
            if not e.finished
        ]

        self.animator.update(dt)
        self._update_footsteps()
        self.rotator.update(
            self,
            dt
        )

        self.hitbox.center = (
            int(self.position.x),
            int(self.position.y)
        )

    def draw_effects(self, screen, camera):
        """Llamar ANTES de player.draw(), junto con blood_decals.draw(),
        para que el shockwave se vea en el piso y no tape al personaje."""
        for effect in self.active_effects:
            effect.draw(
                screen,
                camera
            )

    def draw(self, screen, camera):
        screen_position = camera.world_to_screen(
            self.position
        )

        legs_anim = self.animator.legs_player.animation

        if legs_anim in (
            "frontwalk",
            "run",
            "frontdodge"
        ):
            legs = pygame.transform.rotate(
                self.animator.legs,
                -self.move_angle
            )

            legs_rect = legs.get_rect(
                center=self.position - camera.position
            )

            screen.blit(
                legs,
                legs_rect
            )

        elif legs_anim in (
            "backwalk",
            "backdodge"
        ):
            legs = pygame.transform.rotate(
                self.animator.legs,
                -(self.move_angle + 180)
            )

            legs_rect = legs.get_rect(
                center=self.position - camera.position
            )

            screen.blit(
                legs,
                legs_rect
            )

        else:
            legs = pygame.transform.rotate(
                self.animator.legs,
                -self.aim_angle
            )

            legs_rect = legs.get_rect(
                center=self.position - camera.position
            )

            screen.blit(
                legs,
                legs_rect
            )

        # mientras corre, todo el cuerpo mira hacia donde te movés (no hacia
        # el mouse). En el dodge, igual que al caminar, el cuerpo sigue
        # apuntando al mouse — solo cambian las piernas (front/back)

        is_movement_anim = (
            self.animator.body_player.animation == "run"
        )

        body_angle = (
            self.move_angle
            if is_movement_anim
            else self.aim_angle
        )

        body = pygame.transform.rotate(
            self.animator.torso,
            -body_angle
        )

        body_rect = body.get_rect(
            center=self.position - camera.position
        )

        head = pygame.transform.rotate(
            self.animator.head,
            -body_angle
        )

        head_rect = head.get_rect(
            center=self.position - camera.position
        )

        if self.flash_timer > 0:
            flash_body = body.copy()

            flash_body.fill(
                (255, 60, 60, 255),
                special_flags=pygame.BLEND_RGBA_MULT
            )

            screen.blit(
                flash_body,
                body_rect
            )

            flash_head = head.copy()

            flash_head.fill(
                (255, 60, 60, 255),
                special_flags=pygame.BLEND_RGBA_MULT
            )

            screen.blit(
                flash_head,
                head_rect
            )

        else:
            screen.blit(
                body,
                body_rect
            )

            screen.blit(
                head,
                head_rect
            )

        for b in self.bullets:
            bullet_rect = b.image.get_rect(
                center=b.position - camera.position
            )

            screen.blit(
                b.image,
                bullet_rect
            )