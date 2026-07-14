from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import dashboard

app = FastAPI(
    title="IHP Analytics Service",
    description="Hospital resource utilisation, disease forecasting, and board reporting API.",
    version="0.1.0",
)

# Tighten this to the gateway's origin once the gateway exists — wide open only for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])


@app.get("/healthz")
def healthz():
    """Liveness/readiness probe target for the K8s deployment."""
    return {"status": "ok", "service": "analytics"}
