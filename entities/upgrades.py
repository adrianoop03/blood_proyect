class Upgrade:
    def __init__(self, name, description, apply_fn):
        self.name = name
        self.description = description
        self.apply_fn = apply_fn

    def apply(self, player):
        self.apply_fn(player)


def _add_max_health(amount):
    def fn(player):
        player.max_health += amount
        player.health += amount
    return fn


def _add_max_energy(amount, regen_bonus=0):
    def fn(player):
        player.max_energy += amount
        player.energy += amount
        player.energy_regen_rate += regen_bonus
    return fn


def _mult_speed(factor):
    def fn(player):
        player.base_speed = int(player.base_speed * factor)
    return fn


def _mult_shoot_delay(factor):
    def fn(player):
        player.shoot_delay = max(0.05, player.shoot_delay * factor)
    return fn


def _add_pellets(amount):
    def fn(player):
        player.num_pellets += amount
    return fn


def _reduce_spread(amount):
    def fn(player):
        player.spread_angle = max(5, player.spread_angle - amount)
    return fn


def _mult_sprint_cost(factor):
    def fn(player):
        player.sprint_energy_cost = max(1, player.sprint_energy_cost * factor)
    return fn


def get_upgrade_pool():
    return [
        Upgrade("Vitalidad de Bestia", "+20 de vida máxima", _add_max_health(20)),
        Upgrade("Corazón de Roble", "+35 de vida máxima", _add_max_health(35)),
        Upgrade("Pulmones de Cazador", "+25 energía máxima, regenera más rápido", _add_max_energy(25, regen_bonus=5)),
        Upgrade("Piernas de Lobo", "+15% velocidad al correr", _mult_speed(1.15)),
        Upgrade("Botas Ligeras", "+25% velocidad al correr", _mult_speed(1.25)),
        Upgrade("Puntería Certera", "Recarga 20% más rápida", _mult_shoot_delay(0.8)),
        Upgrade("Gatillo Ágil", "Recarga 35% más rápida", _mult_shoot_delay(0.65)),
        Upgrade("Perdigones Cargados", "+2 perdigones por disparo", _add_pellets(2)),
        Upgrade("Cañón Recortado", "Cono de disparo más cerrado (más preciso)", _reduce_spread(8)),
        Upgrade("Resistencia de Fiera", "Correr consume 20% menos energía", _mult_sprint_cost(0.8)),
    ]
