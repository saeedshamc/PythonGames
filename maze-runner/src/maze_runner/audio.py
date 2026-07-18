import pygame

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class SoundManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}

        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self.enabled = NUMPY_AVAILABLE
        except pygame.error:
            self.enabled = False

        if self.enabled:
            self._build_sounds()

    def _make_tone(self, frequency, duration_ms, volume=0.4, fade_out=True):
        sample_rate = 44100
        n_samples = int(sample_rate * duration_ms / 1000)
        t = np.linspace(0, duration_ms / 1000, n_samples, False)
        wave = np.sin(frequency * t * 2 * np.pi)

        if fade_out:
            fade = np.linspace(1, 0, n_samples)
            wave = wave * fade

        wave = (wave * volume * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(wave)

    def _build_sounds(self):
        try:
            self.sounds["move"] = self._make_tone(220, 40, volume=0.15)
            self.sounds["wall"] = self._make_tone(120, 80, volume=0.2)
            self.sounds["win"] = self._make_tone(660, 300, volume=0.35)
            self.sounds["caught"] = self._make_tone(90, 400, volume=0.35)
            self.sounds["step_enemy"] = self._make_tone(300, 30, volume=0.08)
        except Exception:
            self.enabled = False

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass
