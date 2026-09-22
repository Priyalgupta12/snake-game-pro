"""Small procedural particle system used by the game client."""
import random
import pygame


class Particle:
    def __init__(self, x: float, y: float, color: tuple[int, int, int]):
        self.x, self.y = x, y
        self.dx, self.dy = random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5)
        self.life, self.color = random.randint(18, 36), color

    def update(self) -> bool:
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.06
        self.life -= 1
        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        alpha = max(0, min(255, self.life * 8))
        dot = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*self.color, alpha), (3, 3), 3)
        surface.blit(dot, (self.x - 3, self.y - 3))
