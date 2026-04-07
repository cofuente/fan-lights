#!/usr/bin/env python3
"""
Fan RGB Daemon — auto-discovers patterns and drives the Framework fan LEDs.

Usage:
    sudo python daemon.py                  # lists available patterns
    sudo python daemon.py rainbow          # run a pattern
    sudo python daemon.py rainbow,fire     # cycle patterns (30s each)
"""

import sys
import time
import signal
import subprocess
from patterns import discover
from patterns.base import Pattern

FRAMEWORK_TOOL_PATH = "./framework_tool"
NUM_LEDS = 8
CYCLE_SECONDS = 30  # time per pattern when cycling


def send(colors: list[tuple[int, int, int]]):
    hex_colors = [f"0x{r:02x}{g:02x}{b:02x}" for r, g, b in colors]
    # Pad or trim to NUM_LEDS
    hex_colors = (hex_colors + ["0x000000"] * NUM_LEDS)[:NUM_LEDS]
    cmd = [FRAMEWORK_TOOL_PATH, "--rgbkbd", "0"] + hex_colors
    subprocess.run(cmd, capture_output=True, check=False)


def lights_off():
    send([Pattern.black()] * NUM_LEDS)


def run_pattern(pattern: Pattern):
    while True:
        colors = pattern.step()
        send(colors)
        time.sleep(pattern.delay)


def run_cycle(patterns: list[Pattern]):
    while True:
        for p in patterns:
            print(f"  ▸ {p.NAME}")
            start = time.monotonic()
            while time.monotonic() - start < CYCLE_SECONDS:
                send(p.step())
                time.sleep(p.delay)


def main():
    registry = discover()

    if len(sys.argv) < 2:
        print("Available patterns:")
        for name in sorted(registry):
            print(f"  • {name}")
        print(f"\nUsage: sudo python {sys.argv[0]} <pattern>")
        print(f"       sudo python {sys.argv[0]} <p1>,<p2>   (cycle every {CYCLE_SECONDS}s)")
        return

    # Graceful shutdown: turn lights off on exit
    signal.signal(signal.SIGINT, lambda *_: (lights_off(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda *_: (lights_off(), sys.exit(0)))

    requested = [name.strip() for name in sys.argv[1].split(",")]
    instances = []
    for name in requested:
        if name not in registry:
            print(f"Unknown pattern '{name}'. Available: {', '.join(sorted(registry))}")
            return
        instances.append(registry[name]())

    try:
        if len(instances) == 1:
            print(f"Running: {instances[0].NAME}  (Ctrl-C to stop)")
            run_pattern(instances[0])
        else:
            print(f"Cycling: {', '.join(p.NAME for p in instances)}  (Ctrl-C to stop)")
            run_cycle(instances)
    finally:
        lights_off()


if __name__ == "__main__":
    main()
