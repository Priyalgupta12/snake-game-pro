"""Neon Snake Game Pro client with non-blocking API calls, name entry, and leaderboard sidebar.
Run with: python -m game.main
"""
from __future__ import annotations

import random
import threading
import time
from collections import deque
from typing import Optional

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

        # Player name handling
        self.player_name = "PLAYER"
        self.name_entry_active = False
        self.name_buffer = self.player_name

        # Networking
        self._http_lock = threading.Lock()
        self._load_scores_background()

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
        # ensure name entry is not active when a new game starts
        self.name_entry_active = False

    def random_free_cell(self):
        free = [(x, y) for x in range(COLS) for y in range(ROWS) if (x, y) not in self.snake]
        return random.choice(free)

    def _load_scores_background(self) -> None:
        if not httpx:
            return

        def work():
            try:
                data = httpx.get(f"{API_URL}/api/leaderboard", timeout=1.0).json()
                scores = data.get("scores", [])
                with self._http_lock:
                    self.leaderboard = scores
                    self.best = max([item["score"] for item in self.leaderboard] or [0])
            except Exception:
                # Silent fail; leaderboard is optional
                pass

        threading.Thread(target=work, daemon=True).start()

    def submit_score(self) -> None:
        if not httpx or self.score <= 0:
            return

        player = (self.player_name or "PLAYER").strip()[:20]

        def work(p: str, s: int, lv: int):
            try:
                httpx.post(f"{API_URL}/api/scores", json={"player": p, "score": s, "level": lv}, timeout=1.0)
                # refresh leaderboard after a successful submit
                try:
                    data = httpx.get(f"{API_URL}/api/leaderboard", timeout=1.0).json()
                    with self._http_lock:
                        self.leaderboard = data.get("scores", [])
                        self.best = max([item["score"] for item in self.leaderboard] or [0])
                except Exception:
                    pass
            except Exception:
                pass

        threading.Thread(target=work, args=(player, self.score, self.level), daemon=True).start()

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
            # prompt for name entry on game over
            self.name_entry_active = True
            self.name_buffer = self.player_name
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

    def _draw_sidebar(self) -> None:
        t = self.theme
        sidebar_w = 220
        sidebar_rect = pygame.Rect(WIDTH - sidebar_w - 24, ORIGIN[1], sidebar_w, ROWS * CELL)
        pygame.draw.rect(self.screen, t["panel"], sidebar_rect, border_radius=10)
        pygame.draw.rect(self.screen, t["accent"], sidebar_rect, 2, border_radius=10)
        self.text("LEADERBOARD", (sidebar_rect.x + 18, sidebar_rect.y + 12), 20, t["accent"])
        with self._http_lock:
            entries = list(self.leaderboard)
        for i, entry in enumerate(entries[:6]):
            y = sidebar_rect.y + 44 + i * 34
            name = entry.get("player", "PLAYER")[:16]
            score = entry.get("score", 0)
            self.text(f"{i+1}. {name}", (sidebar_rect.x + 18, y), 18, t["head"])
            self.text(f"{score:5d}", (sidebar_rect.right - 34, y), 18, t["food"]) 

    def draw(self) -> None:
        t = self.theme
        # animated background (subtle vertical gradient)
        top = t["bg"]
        bottom = tuple(min(255, c + 22) for c in t["panel"])
        for y in range(0, HEIGHT, 4):
            k = y / HEIGHT
            color = tuple(int(top[i] * (1 - k) + bottom[i] * k) for i in range(3))
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y), 1)

        self.text("S N A K E  //  G A M E  P R O", (38, 28), 28, t["head"])
        self.text(f"THEME: {t['name']}   [T]", (WIDTH - 300, 34), 18, t["accent"])
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

        # sidebar
        self._draw_sidebar()

        if self.paused or self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((2, 3, 14, 200))
            self.screen.blit(overlay, (0, 0))
            title = "GAME OVER" if self.game_over else "PAUSED"
            self.text(title, (WIDTH // 2, HEIGHT // 2 - 32), 62, t["head"], center=True)
            subtitle = "Press R to run it back" if self.game_over else "Press P or SPACE to continue"
            self.text(subtitle, (WIDTH // 2, HEIGHT // 2 + 25), 24, t["accent"], center=True)

        # name-entry overlay
        if self.name_entry_active:
            box_w, box_h = 520, 110
            box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box.fill((8, 10, 28, 230))
            rect = box.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 110))
            pygame.draw.rect(box, t["panel"], (0, 0, box_w, box_h), border_radius=8)
            pygame.draw.rect(box, t["accent"], (0, 0, box_w, box_h), 2, border_radius=8)
            self.screen.blit(box, rect.topleft)
            self.text("ENTER PLAYER NAME:", (rect.x + 20, rect.y + 12), 20, t["accent"])
            display = self.name_buffer + ("|" if int(time.time() * 2) % 2 == 0 else "")
            self.text(display, (rect.x + 20, rect.y + 48), 32, t["head"]) 

        self.text("WASD / ARROWS  MOVE     P / SPACE  PAUSE     ESC  QUIT", (WIDTH // 2, HEIGHT - 24), 18, (135, 145, 190), center=True)
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # if the user is editing their name, capture text input
                    if self.name_entry_active:
                        if event.key == pygame.K_RETURN:
                            # save name and close entry
                            self.player_name = self.name_buffer.strip()[:20] or "PLAYER"
                            self.name_entry_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.name_buffer = self.name_buffer[:-1]
                        else:
                            ch = event.unicode
                            if ch and ch.isprintable() and len(self.name_buffer) < 20:
                                self.name_buffer += ch
                        continue

                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.change_direction((0, -1))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.change_direction((0, 1))
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.change_direction((-1, 0))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.change_direction((1, 0))
                    elif event.key in (pygame.K_p, pygame.K_SPACE) and not self.game_over:
                        self.paused = not self.paused
                    elif event.key == pygame.K_t:
                        self.theme_index = (self.theme_index + 1) % len(THEMES)
                    elif event.key == pygame.K_r and self.game_over:
                        # restart the game; keep the entered player name
                        self.reset()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()


def main() -> None:
    SnakeGame().run()


if __name__ == "__main__":
    main()
