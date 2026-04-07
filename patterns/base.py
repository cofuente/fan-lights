import colorsys

class Pattern:
    """Base class for all LED patterns. Subclass and implement step()."""

    NAME = "unnamed"
    NUM_LEDS = 8

    def __init__(self):
        self.tick = 0

    def step(self) -> list[tuple[int, int, int]]:
        """Return a list of NUM_LEDS (r, g, b) tuples (0-255 each)."""
        raise NotImplementedError

    @property
    def delay(self) -> float:
        """Seconds between updates. Override to change speed."""
        return 0.05

    # ── Helpers available to all patterns ──

    @staticmethod
    def hsv(h, s=1.0, v=1.0) -> tuple[int, int, int]:
        r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

    @staticmethod
    def lerp_color(c1, c2, t):
        """Linear interpolate between two (r,g,b) tuples. t in [0,1]."""
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

    @staticmethod
    def black():
        return (0, 0, 0)
