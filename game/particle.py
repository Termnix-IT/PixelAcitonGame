from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pyxel


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: int
    life: int
    gravity: float = 0.08
    drag: float = 0.96

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= self.drag
        self.life -= 1

    @property
    def alive(self) -> bool:
        return self.life > 0

    def draw(self) -> None:
        pyxel.pset(int(self.x), int(self.y), self.color)


def spawn_burst(
    particles: list[Particle],
    cx: float,
    cy: float,
    color: int = 14,
    count: int = 12,
) -> None:
    """Radial burst of short-lived dots with upward bias and mild gravity."""
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.5, 1.8)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 0.4
        particles.append(
            Particle(cx, cy, vx, vy, color, random.randint(18, 28))
        )
