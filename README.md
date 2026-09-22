# Snake Game Pro

A polished, neon arcade Snake game built with **Python + Pygame**, backed by a lightweight **FastAPI REST API** and SQLite leaderboard. It includes procedural visuals, particles, power-ups, dynamic difficulty, themes, pause/resume, and a professional local development setup.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white) ![Pygame](https://img.shields.io/badge/Game-Pygame-00A86B) ![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)

## Features

- Smooth neon arcade presentation with animated gradient background, glow, grid, particles, screen shake, and food pulse effects.
- Classic keyboard controls plus pause, restart, theme switching, and a name-entry flow.
- Dynamic difficulty: the game speeds up as the snake grows and supports three modes.
- Power-ups: **golden fruit** gives bonus points and **cyan boost** temporarily slows the game.
- Local REST API for health checks, score submission, leaderboard retrieval, and stats.
- SQLite persistence with validation and CORS enabled for future web clients.
- No image assets required—the entire visual style is generated in code.

## Quick start

```bash
# 1. Clone and enter the project
git clone https://github.com/Priyalgupta12/snake-game-pro.git
cd snake-game-pro

# 2. Create a virtual environment
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the API (terminal 1)
uvicorn api.main:app --reload

# 5. Start the game (terminal 2)
python -m game.main
```

The API runs at `http://127.0.0.1:8000`; interactive documentation is at `/docs`. If the API is not running, the game still works offline and records the score locally for the current session.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys / WASD | Move |
| P / Space | Pause or resume |
| R | Restart after game over |
| T | Change visual theme |
| Esc | Quit |

## API

- `GET /health` — service status
- `GET /api/leaderboard?limit=10` — highest scores
- `POST /api/scores` — submit `{ "player": "Priya", "score": 120, "level": 4 }`
- `GET /api/stats` — aggregate score statistics

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/scores \\
  -H "Content-Type: application/json" \\
  -d '{"player":"Priya","score":120,"level":4}'
```

## Project structure

```text
snake-game-pro/
├── api/                 # FastAPI application and SQLite repository
│   ├── main.py
│   └── database.py
├── game/                # Pygame client
│   ├── main.py
│   ├── config.py
│   └── effects.py
├── requirements.txt
└── README.md
```

## Configuration

Optional environment variables:

- `SNAKE_API_URL` — API base URL (default `http://127.0.0.1:8000`)
- `SNAKE_DB_PATH` — SQLite file location (default `snake_scores.db`)

## License

MIT. Have fun and make it your own!