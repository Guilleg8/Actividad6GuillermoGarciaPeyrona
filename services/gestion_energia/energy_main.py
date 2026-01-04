import asyncio
import logging
import httpx
import os
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    def setup_telemetry(app, name): pass

SERVICE_NAME = "gestion_energia"
SERVICE_PORT = int(os.getenv("PORT", 8002))
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://service_registry:8000/register")

class EnergyReport(BaseModel):
    zone_id: str
    consumption_kwh: float

grid_status = {
    "status": "STABLE",
    "total_load_mw": 450.5,
    "renewable_contribution_percent": 32.0
}

async def register_service():
    await asyncio.sleep(3)
    async with httpx.AsyncClient() as client:
        try:
            my_url = f"http://{SERVICE_NAME}:{SERVICE_PORT}"
            await client.post(REGISTRY_URL, json={
                "service_name": SERVICE_NAME, "url": my_url, "health_url": f"{my_url}/health"
            })
            logging.info(f"✅ {SERVICE_NAME} Registrado")
        except Exception:
            logging.error(f"⚠️ Fallo registro {SERVICE_NAME}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(register_service())
    yield

app = FastAPI(lifespan=lifespan, title="Wakanda Energy")
setup_telemetry(app, SERVICE_NAME)

@app.get("/energy/grid")
async def get_grid_status():
    return grid_status

@app.post("/energy/report")
async def report_consumption(report: EnergyReport):
    grid_status["total_load_mw"] += (report.consumption_kwh / 1000)
    return {"status": "received", "new_load": grid_status["total_load_mw"]}

@app.get("/health")
async def health(): return {"status": "ok"}