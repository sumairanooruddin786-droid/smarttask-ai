"""SmartTask AI - FastAPI server (serves the API and the frontend)."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .graph import organize
from .schemas import OrganizeRequest, OrganizeResponse

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(title="SmartTask AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/organize", response_model=OrganizeResponse)
def organize_tasks(req: OrganizeRequest):
    try:
        state = organize(req.message)
    except RuntimeError as exc:           # e.g. missing API key
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:              # Gemini / network errors
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}")
    return OrganizeResponse(
        tasks=state.get("prioritized", []), formatted=state.get("output", "")
    )


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
