import asyncio
import logging
import random
import httpx
import os
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gestion_trafico")

try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    logger.warning("⚠️ No se encontró wakanda_shared. La telemetría estará desactivada.")


    def setup_telemetry(app, name):
        pass

SERVICE_NAME = "gestion_trafico"
SERVICE_PORT = int(os.getenv("PORT", 8001))
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://service_registry:8000/register")


class TrafficAdjustment(BaseModel):
    new_green_seconds: int


class TrafficStatus(BaseModel):
    intersection_id: str
    timestamp: str
    vehicle_count: int
    average_speed_kmh: float
    signal_phase: str
    recommended_adjustment: TrafficAdjustment


class TrafficUpdate(BaseModel):
    intersection_id: str
    duration: int


SIMULATION_RUNNING = False
CURRENT_GREEN_DURATION = 30

current_status = TrafficStatus(
    intersection_id="I-12",
    timestamp=datetime.utcnow().isoformat(),
    vehicle_count=0,
    average_speed_kmh=0.0,
    signal_phase="RED",
    recommended_adjustment=TrafficAdjustment(new_green_seconds=30)
)


async def simulate_traffic_cycle():
    global current_status
    phases = ["RED", "GREEN", "YELLOW"]
    while SIMULATION_RUNNING:
        vehicle_count = random.randint(0, 50)
        speed = max(5.0, 60.0 - vehicle_count * 0.8) if vehicle_count > 0 else 0.0
        current_phase = random.choice(phases)

        current_status = TrafficStatus(
            intersection_id="I-12",
            timestamp=datetime.utcnow().isoformat(),
            vehicle_count=vehicle_count,
            average_speed_kmh=round(speed, 2),
            signal_phase=current_phase,
            recommended_adjustment=TrafficAdjustment(new_green_seconds=CURRENT_GREEN_DURATION)
        )
        logger.debug(f"Simulación: {vehicle_count} vehículos, Fase {current_phase}")
        await asyncio.sleep(3)


async def register_service():
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "service_name": SERVICE_NAME,
                "url": f"http://gestion_trafico:{SERVICE_PORT}",
                "health_url": f"http://gestion_trafico:{SERVICE_PORT}/health"
            }
            await client.post(REGISTRY_URL, json=payload, timeout=5.0)
            logger.info(f"✅ Registrado en {REGISTRY_URL}")
        except Exception as e:
            logger.error(f"❌ Fallo al registrar: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global SIMULATION_RUNNING
    SIMULATION_RUNNING = True
    task = asyncio.create_task(simulate_traffic_cycle())
    asyncio.create_task(register_service())

    yield

    SIMULATION_RUNNING = False
    task.cancel()


app = FastAPI(title="Gestión Tráfico", lifespan=lifespan)

setup_telemetry(app, SERVICE_NAME)


@app.get("/health")
def health(): return {"status": "ok"}


@app.get("/status", response_model=TrafficStatus)
def get_status(): return current_status


@app.post("/adjust_signal")
def adjust(update: TrafficUpdate):
    global CURRENT_GREEN_DURATION
    CURRENT_GREEN_DURATION = update.duration
    return {"status": "updated", "new_duration": update.duration}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)