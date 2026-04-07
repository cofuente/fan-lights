from patterns.base import Pattern

class Rainbow(Pattern):
    NAME = "rainbow"

    def step(self):
        self.tick += 1
        offset = self.tick * 0.02
        return [self.hsv(offset + i / self.NUM_LEDS) for i in range(self.NUM_LEDS)]
