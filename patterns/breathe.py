import math
from patterns.base import Pattern

class Breathe(Pattern):
    """Gentle breathing pulse in a single color."""
    NAME = "breathe"

    def __init__(self, hue=0.55):
        super().__init__()
        self.hue = hue

    @property
    def delay(self):
        return 0.03

    def step(self):
        self.tick += 1
        brightness = (math.sin(self.tick * 0.04) + 1) / 2  # 0..1
        color = self.hsv(self.hue, 1.0, brightness)
        return [color] * self.NUM_LEDS
