import random
from patterns.base import Pattern

class Fire(Pattern):
    """Warm flickering fire effect."""
    NAME = "fire"

    @property
    def delay(self):
        return 0.06

    def step(self):
        colors = []
        for _ in range(self.NUM_LEDS):
            # Hue 0.0-0.08 gives red-orange-yellow range
            hue = random.uniform(0.0, 0.08)
            brightness = random.uniform(0.3, 1.0)
            colors.append(self.hsv(hue, 1.0, brightness))
        return colors
