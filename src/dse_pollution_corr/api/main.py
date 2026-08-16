"""FastAPI application for the DSE analysis agent."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dse_pollution_corr.agent.agent import run_agent
from dse_pollution_corr.db.load_db import rebuild_database
from dse_pollution_corr.paths import db_path


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    sql: str | None = None
    chart: dict | None = None
    preview: dict | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_dotenv()
    if os.environ.get("AUTO_BUILD_DB", "true").lower() in {"1", "true", "yes"}:
        if not db_path().exists():
            rebuild_database()
    yield


app = FastAPI(title="DSE Pollution Analysis Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": str(db_path().exists())}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not db_path().exists():
        raise HTTPException(status_code=503, detail="Database not built. Run load-dse-db first.")
    try:
        result = run_agent(request.message)
    except Exception as exc:  # noqa: BLE001 - surface agent errors to client
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(**result)


@app.post("/api/admin/rebuild-db")
def admin_rebuild_db() -> dict[str, str]:
    path = rebuild_database()
    return {"status": "ok", "path": str(path)}


def run() -> None:
    import uvicorn

    load_dotenv()
    uvicorn.run(
        "dse_pollution_corr.api.main:app",
        host=os.environ.get("API_HOST", "127.0.0.1"),
        port=int(os.environ.get("API_PORT", "8000")),
        reload=os.environ.get("API_RELOAD", "true").lower() in {"1", "true", "yes"},
    )
