"""Snake Game Pro REST endpoints."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from .database import add_score, init_db, leaderboard, stats


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Snake Game Pro API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ScoreIn(BaseModel):
    player: str = Field(default="PLAYER", min_length=1, max_length=20)
    score: int = Field(ge=0, le=10_000_000)
    level: int = Field(default=1, ge=1, le=999)

    @field_validator("player")
    @classmethod
    def clean_player(cls, value: str) -> str:
        return " ".join(value.strip().split()) or "PLAYER"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "snake-game-pro-api"}


@app.get("/api/leaderboard")
def get_leaderboard(limit: int = Query(10, ge=1, le=100)) -> dict:
    return {"scores": leaderboard(limit)}


@app.post("/api/scores", status_code=201)
def post_score(payload: ScoreIn) -> dict:
    return {"score": add_score(payload.player, payload.score, payload.level)}


@app.get("/api/stats")
def get_stats() -> dict:
    return stats()
