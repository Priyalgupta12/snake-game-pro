"""Neon Snake Game Pro client. Run with: python -m game.main"""
from __future__ import annotations

import random
import threading
import time
from collections import deque

import pygame

from .config import API_URL, CELL, COLS, HEIGHT, ORIGIN, ROWS, THEMES, WIDTH
from .effects import Particle

try:
    import httpx
except ImportError:
    httpx = None


class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("SNAKE // GAME PRO")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 26)
        self.big = pygame.font.Font(None, 58)
        self.small = pygame.font.Font(None, 20)
        self.theme_index = 0
        self.best = 0
        self.leaderboard: list[dict] = []
        self.load_scores()
        self.reset()

    @property
    def theme(self):
        return THEMES[self.theme_index]

    def reset(self) -> None:
        mid = (COLS // 2, ROWS // 2)
        self.snake = deque([(mid[0] - i, mid[1]) for i in range(5)])
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.random_free_cell()
        self.powerup = None
        self.power_kind = ""
        self.particles: list[Particle] = []
        self.score, self.level = 0, 1
        self.started = time.monotonic()
        self.last_step = self.started
        self.paused, self.game_over = False, False
        self.shake = 0

    def random_free_cell(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in self.snake]
        return random.choice(free)

    def load_scores(self) -> None:
        if not httpx:
            return
        try:
            data = httpx.get(f"{API_URL}/api/leaderboard", timeout=0.6).json()
            self.leaderboard = data.get("scores", [])
            self.best = max([item["score"] for item in self.leaderboard] or [0])
        except Exception:
            pass

    def submit_score(self) -> None:
        if not httpx or self.score <= 0:
            return
        try:
            httpx.post(f"{API_URL}/api/scores", json={"player": "PLAYER", "score": self.score, "level": self.level}, timeout=0.8)
        except Exception:
            pass

    def change_direction(self, direction: tuple[int, int]) -> None:
        if direction[0] + self.direction[0] != 0 or direction[1] + self.direction[1] != 0:
            self.next_direction = direction

    def step(self) -> None:
        self.direction = self.next_direction
        head = self.snake[0]
        new = (head[0] + self.direction[0], head[1] + self.direction[1])
        if new[0] < 0 or new[0] >= COLS or new[1] < 0 or new[1] >= ROWS or new in self.snake:
            self.game_over = True
            self.shake = 14
            self.submit_score()
            return
        self.snake.appendleft(new)
        eaten = new == self.food
        if eaten:
            self.score += 10 * self.level
            self.level = 1 + self.score // 100
            self.food = self.random_free_cell()
            self.shake = 3
            px, py = self.cell_center(new)
            self.particles += [Particle(px, py, self.theme["food"]) for _ in range(16)]
            if random.random() < 0.22:
                self.powerup = self.random_free_cell()
                self.power_kind = random.choice(["BOOST", "BONUS"])
        else:
            self.snake.pop()
        if self.powerup and new == self.powerup:
            self.score += 50 if self.power_kind == "BONUS" else 20
            self.powerup = None

    def cell_center(self, cell):
        return (ORIGIN[0] + cell[0] * CELL + CELL // 2, ORIGIN[1] + cell[1] * CELL + CELL // 2)

    def update(self) -> None:
        now = time.monotonic()
        speed = max(0.055, 0.14 - self.level * 0.006)
        if not self.paused and not self.game_over and now - self.last_step >= speed:
            self.step()
            self.last_step = now
        self.particles = [p for p in self.particles if p.update()]
        self.shake = max(0, self.shake - 1)

    def text(self, value, position, size=None, color=(220, 225, 255), center=False):
        font = self.font if size is None else pygame.font.Font(None, size)
        image = font.render(str(value), True, color)
        rect = image.get_rect(center=position) if center else image.get_rect(topleft=position)
        self.screen.blit(image, rect)

    def draw(self) -> None:
        t = self.theme
        self.screen.fill(t["bg"])
        # Atmospheric stripes
        for y in range(0, HEIGHT, 4):
            color = tuple(min(255, c + (y // 80)) for c in t["bg"])
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y), 1)
        self.text("S N A K E  //  G A M E  P R O", (38, 28), 28, t["head"])
        self.text(f"THEME: {t['name']}   [T]", (WIDTH - 230, 34), 18, t["accent"])
        self.text(f"SCORE  {self.score:05d}", (38, 74), 22, t["snake"])
        self.text(f"BEST  {max(self.best, self.score):05d}", (210, 74), 22, t["accent"])
        self.text(f"LEVEL {self.level:02d}", (360, 74), 22, t["food"])
        bx, by = ORIGIN
        board = pygame.Rect(bx - 8, by - 8, COLS * CELL + 16, ROWS * CELL + 16)
        pygame.draw.rect(self.screen, t["panel"], board, border_radius=14)
        pygame.draw.rect(self.screen, t["accent"], board, 2, border_radius=14)
        for x in range(COLS + 1):
            pygame.draw.line(self.screen, t["grid"], (bx + x * CELL, by), (bx + x * CELL, by + ROWS * CELL))
        for y in range(ROWS + 1):
            pygame.draw.line(self.screen, t["grid"], (bx, by + y * CELL), (bx + COLS * CELL, by + y * CELL))
        # Food glow and fruit
        fx, fy = self.cell_center(self.food)
        pulse = 8 + int(3 * (1 + __import__("math").sin(time.monotonic() * 5)))
        pygame.draw.circle(self.screen, (*t["food"], 45), (fx, fy), pulse + 7)
        pygame.draw.circle(self.screen, t["food"], (fx, fy), pulse // 2 + 2)
        if self.powerup:
            px, py = self.cell_center(self.powerup)
            color = (255, 211, 82) if self.power_kind == "BONUS" else (74, 222, 255)
            pygame.draw.circle(self.screen, color, (px, py), 8, 2)
            self.text("★", (px, py - 1), 18, color, center=True)
        for i, cell in enumerate(self.snake):
            x, y = bx + cell[0] * CELL + 3, by + cell[1] * CELL + 3
            color = t["head"] if i == 0 else t["snake"]
            pygame.draw.rect(self.screen, color, (x, y, CELL - 6, CELL - 6), border_radius=7 if i == 0 else 4)
            if i == 0:
                ex = x + (15 if self.direction[0] >= 0 else 6)
                pygame.draw.circle(self.screen, t["panel"], (ex, y + 7), 2)
        for particle in self.particles:
            particle.draw(self.screen)
        if self.paused or self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((2, 3, 14, 170))
            self.screen.blit(overlay, (0, 0))
            title = "GAME OVER" if self.game_over else "PAUSED"
            self.text(title, (WIDTH // 2, HEIGHT // 2 - 32), 62, t["head"], center=True)
            subtitle = "Press R to run it back" if self.game_over else "Press P or SPACE to continue"
            self.text(subtitle, (WIDTH // 2, HEIGHT // 2 + 25), 24, t["accent"], center=True)
        self.text("WASD / ARROWS  MOVE     P / SPACE  PAUSE     ESC  QUIT", (WIDTH // 2, HEIGHT - 24), 18, (135, 145, 190), center=True)
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_UP, pygame.K_w): self.change_direction((0, -1))
                    elif event.key in (pygame.K_DOWN, pygame.K_s): self.change_direction((0, 1))
                    elif event.key in (pygame.K_LEFT, pygame.K_a): self.change_direction((-1, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): self.change_direction((1, 0))
                    elif event.key in (pygame.K_p, pygame.K_SPACE) and not self.game_over: self.paused = not self.paused
                    elif event.key == pygame.K_t: self.theme_index = (self.theme_index + 1) % len(THEMES)
                    elif event.key == pygame.K_r and self.game_over: self.reset()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()


def main() -> None:
    SnakeGame().run()


if __name__ == "__main__":
    main()
