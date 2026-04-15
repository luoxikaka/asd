from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="user-service", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "user-service"}
