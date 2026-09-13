"""
FastAPI Main Application Entrypoint — FIFA World Cup Prediction API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.prediction import router as prediction_router
from backend.app.services.predictor import PredictorService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize singleton predictor service on startup
    print("[STARTUP] Pre-warming PredictorService ML models...")
    PredictorService.get_instance()
    print("[STARTUP] Models loaded and ready to serve traffic.")
    yield
    print("[SHUTDOWN] Cleaning up resources...")


app = FastAPI(
    title="FIFA World Cup 2026 Prediction API",
    description="REST API service providing ML match forecasts, Monte Carlo tournament simulations, and team analytics.",
    version="2.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend clients (React / Vite / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(prediction_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "FIFA World Cup Prediction API",
        "version": "2.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
