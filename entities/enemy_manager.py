class EnemyManager:

    def __init__(self, max_concurrent_attackers=3):
        self.max_concurrent_attackers = max_concurrent_attackers
        self.engaged = set()

    def request_engage(self, enemy):
        if enemy in self.engaged:
            return True
        if len(self.engaged) < self.max_concurrent_attackers:
            self.engaged.add(enemy)
            return True
        return False

    def release(self, enemy):
        self.engaged.discard(enemy)

    def get_slot_angle(self, enemy, all_enemies):
        alive = [e for e in all_enemies if e.alive()]
        if enemy not in alive:
            return 0
        index = alive.index(enemy)
        count = len(alive)
        return (360 / max(count, 1)) * index