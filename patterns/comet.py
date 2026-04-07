from patterns.base import Pattern

class Comet(Pattern):
    """A bright dot chasing around with a fading trail."""
    NAME = "comet"

    def __init__(self, hue=0.6):
        super().__init__()
        self.hue = hue

    def step(self):
        self.tick += 1
        head = self.tick % self.NUM_LEDS
        colors = []
        for i in range(self.NUM_LEDS):
            # Distance behind the head (wrapping)
            dist = (head - i) % self.NUM_LEDS
            brightness = max(0, 1.0 - dist * 0.25)
            colors.append(self.hsv(self.hue, 1.0, brightness))
        return colors

    @property
    def delay(self):
        return 0.08
