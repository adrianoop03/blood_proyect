import pygame
import random
import os


class SoundManager:
    """Estructura esperada:
        assets/sounds/attack1/*.mp3
        assets/sounds/attack2/*.mp3
        assets/sounds/attack3/*.mp3
        assets/sounds/shoot/*.mp3
        assets/sounds/dodge/*.mp3
        assets/sounds/heal/*.mp3
        assets/sounds/hit/*.mp3
        assets/sounds/hurt/*.mp3
        assets/sounds/footsteps_walk/*.mp3
        assets/sounds/footsteps_run/*.mp3"""

    def __init__(self, sound_root="assets/sounds", master_volume=1.0, num_channels=16):
        pygame.mixer.set_num_channels(num_channels)

        self.sounds_by_category = self._load_categories(sound_root)
        self.master_volume = master_volume
        self.category_volumes = {}  # categoria -> multiplicador (0..1)
        self.footstep_channel = pygame.mixer.Channel(0)

    def _load_categories(self, root):
        categories = {}
        if not os.path.isdir(root):
            return categories

        for entry in os.listdir(root):
            full_path = os.path.join(root, entry)
            if os.path.isdir(full_path):
                categories[entry] = self._load_sounds(full_path)

        return categories

    def _load_sounds(self, folder):
        sounds = []
        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith((".mp3", ".ogg")):
                sounds.append(pygame.mixer.Sound(os.path.join(folder, filename)))
        return sounds

    def set_category_volume(self, category, volume):
        self.category_volumes[category] = volume

    def _resolve_volume(self, category, volume_override):
        base = self.category_volumes.get(category, 1.0)
        vol = base * self.master_volume
        if volume_override is not None:
            vol *= volume_override
        return max(0.0, min(1.0, vol))

    def play(self, category, volume=None):
        """Sonido de un solo golpe (ataque, disparo, dodge, etc). Elige una
        variante al azar entre las disponibles en esa categoria."""
        sounds = self.sounds_by_category.get(category)
        if not sounds:
            return

        sound = random.choice(sounds)
        sound.set_volume(self._resolve_volume(category, volume))
        sound.play()

    def play_footstep(self, category, volume=None):
        """Sonido de paso: usa el canal dedicado, asi un paso nuevo
        reemplaza al anterior en vez de superponerse."""
        sounds = self.sounds_by_category.get(category)
        if not sounds:
            return

        sound = random.choice(sounds)
        sound.set_volume(self._resolve_volume(category, volume))
        self.footstep_channel.play(sound)
