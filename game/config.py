"""Configuration and color palettes for the Pygame client."""
import os

WIDTH, HEIGHT = 1000, 720
CELL = 24
COLS, ROWS = 32, 24
BOARD = (COLS * CELL, ROWS * CELL)
ORIGIN = ((WIDTH - BOARD[0]) // 2, 112)
API_URL = os.getenv("SNAKE_API_URL", "http://127.0.0.1:8000")

THEMES = [
    {"name": "CYBERPUNK", "bg": (8, 10, 28), "panel": (17, 20, 49), "grid": (28, 32, 68), "snake": (62, 246, 174), "head": (174, 255, 225), "food": (255, 78, 130), "accent": (91, 123, 255)},
    {"name": "SUNSET", "bg": (29, 13, 30), "panel": (55, 25, 48), "grid": (85, 34, 63), "snake": (255, 191, 71), "head": (255, 240, 177), "food": (255, 80, 86), "accent": (211, 91, 255)},
    {"name": "OCEAN", "bg": (5, 24, 35), "panel": (9, 45, 61), "grid": (14, 67, 82), "snake": (64, 222, 255), "head": (198, 250, 255), "food": (255, 204, 92), "accent": (54, 137, 255)},
]
