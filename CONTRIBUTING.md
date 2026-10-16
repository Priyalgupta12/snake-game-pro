# Contributing to Snake Game Pro

Thanks for your interest in contributing! This project is intentionally small and focused — the fastest way to get changes accepted is to open small, well-scoped PRs with a clear purpose (bug fix, polish, new feature).

How to contribute

- Fork the repository and create a branch for your change (feature/<name> or fix/<short-desc>).
- Keep changes small and focused; one feature or bug per PR.
- Include screenshots/GIFs for visual changes and a short description of how to test your change.
- Ensure your commit messages are clear and follow the conventional style (e.g., `feat:`, `fix:`, `chore:`).

Running the project locally

1. Clone and create a virtual environment:

```bash
git clone https://github.com/Priyalgupta12/snake-game-pro.git
cd snake-game-pro
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the API in one terminal:

```bash
uvicorn api.main:app --reload
```

3. Start the game client in a second terminal:

```bash
python -m game.main
```

Testing and linting

- This repository uses ruff for linting (recommended locally):

```bash
pip install ruff
ruff check .
```

Reporting issues

- Open an issue with a clear title, reproduction steps, and environment details (OS, Python version).

Pull request checklist

- [ ] My changes are small and focused
- [ ] I added or updated documentation where applicable (README, comments)
- [ ] Visual changes include screenshots or a short GIF
- [ ] The PR title follows a conventional prefix (feat/fix/docs/chore)
