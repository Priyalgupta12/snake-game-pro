# Snake Game Pro

A polished, neon-arcade Snake game with procedural visuals, a local FastAPI leaderboard, and easy local deployment.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white) ![Pygame](https://img.shields.io/badge/Game-Pygame-00A86B) ![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)

A fast, focused single-player Snake experience with modern visual effects (animated gradients, glow, particles, screen shake), power-ups, and a lightweight REST API + SQLite backend to save and query high scores.

Demo

> Add an animated GIF or short screencast here (rename assets/screencast.gif and reference the path). A `media/` folder works well for project screenshots.

## Stack
- Language: Python 3.10+
- Frameworks: Pygame (client), FastAPI (server)
- Notable libraries: httpx (client HTTP), pydantic (validation), uvicorn (ASGI server)

## Highlights / Features
- Vibrant, procedural neon themes (3 built-in palettes) with animated background, glow, grid, and particle effects.
- Classic snake gameplay with dynamic difficulty that speeds up as you score.
- Power-ups: bonus fruit and temporary boosts.
- Local FastAPI backend: health checks, score submission, leaderboard, and statistics stored in SQLite.
- No external image assets required — visuals are generated in code.

## Quick start (shortest path)

```bash
# Clone
git clone https://github.com/Priyalgupta12/snake-game-pro.git
cd snake-game-pro

# Python venv (recommended)
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate

pip install -r requirements.txt

# Terminal 1: start the API
uvicorn api.main:app --reload

# Terminal 2: start the game client
python -m game.main
```

The API runs at http://127.0.0.1:8000 (interactive docs: /docs). The game will work offline without the API but leaderboard sync requires the API to be running.

## How it fits together

```
snake-game-pro/
├── api/                 # FastAPI application and SQLite persistence (init, add_score, leaderboard)
│   ├── main.py          # route definitions and Pydantic models
│   └── database.py      # simple SQLite helpers
├── game/                # Pygame client
│   ├── main.py          # game loop, rendering, input, leaderboard integration
│   ├── config.py        # screen, grid, themes, API URL
│   └── effects.py       # particle system
├── requirements.txt
└── README.md
```

## Configuration
Environment variables (optional):
- SNAKE_API_URL — API base URL (default `http://127.0.0.1:8000`)
- SNAKE_DB_PATH — SQLite file location for the server (default `snake_scores.db`)

## Controls
- Arrow keys / WASD — move
- P / Space — pause / resume
- R — restart after game over
- T — cycle visual theme
- Esc — quit

## API (local endpoints)
- GET /health — service status
- GET /api/leaderboard?limit=10 — highest scores
- POST /api/scores — submit { "player": "Priya", "score": 120, "level": 4 }
- GET /api/stats — aggregate score statistics

Example submission:

```bash
curl -X POST http://127.0.0.1:8000/api/scores \
  -H "Content-Type: application/json" \
  -d '{"player":"Priya","score":120,"level":4}'
```

## Development notes & suggestions (quick wins)
These are optional small improvements that will make the project more professional and maintainable.

- Add an in-game name-entry dialog to let players submit their chosen name to the API (instead of the static "PLAYER").
- Fetch the leaderboard periodically (or after game over) and render a small sidebar of top scores in the Pygame client.
- Move HTTP calls off the main thread (use a background thread / AsyncClient) so network hiccups don't drop frames.
- Add unit tests for the API data layer (api/database.py) and a small CI workflow (GitHub Actions) to run lint/tests on PRs.
- Add a small Dockerfile for the API and a docker-compose.yml to run API + client for quick demos.
- Include a `media/` folder with a GIF and a few screenshots; update the README demo section with those assets.

## Contributing
If you'd like to contribute, please read CONTRIBUTING.md (added to this repo). Small PRs with focused changes are easiest to review — e.g. polish visuals, add a theme, or add a new backend endpoint.

## License
MIT — see LICENSE file.
