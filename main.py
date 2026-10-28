import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .models import Base, engine, get_db
from .services.seed_data import seed_database_if_empty
from .api import (
    projects,
    overview,
    revisions,
    adaptation,
    audits,
    tests,
    fixes,
    reports,
    settings
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    # Seed sample projects with baseline audits if empty
    db = next(get_db())
    try:
        seed_database_if_empty(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="AccessCraft API",
    description="Adaptive Accessibility Interface Generator & Automated Verification Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(overview.router)
app.include_router(projects.router)
app.include_router(revisions.router)
app.include_router(adaptation.router)
app.include_router(audits.router)
app.include_router(tests.router)
app.include_router(fixes.router)
app.include_router(reports.router)
app.include_router(settings.router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AccessCraft Backend Engine",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
