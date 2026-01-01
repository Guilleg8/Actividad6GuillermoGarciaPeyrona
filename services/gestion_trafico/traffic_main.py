import asyncio
import logging
import random
import httpx
import os
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Intentamos importar la telemetría compartida
try:
    from wakanda_shared.telemetry import setup_telemetry
except ImportError:
    def setup_telemetry(app, name):
        pass

# --- Configuración ---
SERVICE_NAME = "gestion_trafico"
SERVICE_PORT = int(os.getenv("PORT", 8001))
# En Docker, el registry será accesible por su nombre de servicio "service_registry"
REGISTRY_URL = os.getenv("REGISTRY_URL", "http://service_registry:8000/register")


# --- Modelos de Datos (Pydantic) ---
class TrafficAdjustment(BaseModel):
    new_green_seconds: int


class TrafficStatus(BaseModel):
    intersection_id: str
    timestamp: str
    vehicle_count: int
    average_speed_kmh: float
    signal_phase: str
    recommended_adjustment: TrafficAdjustment


# --- Estado Global (Simulado) ---
# Variable compartida que el "sensor" actualiza y la API lee
current_status = TrafficStatus(
    intersection_id="I-12",
    timestamp=datetime.utcnow().isoformat(),
    vehicle_count=0,
    average_speed_kmh=0.0,
    signal_phase="RED",
    recommended_adjustment=TrafficAdjustment(new_green_seconds=30)
)


# --- Tareas en Segundo Plano (Concurrencia) ---
async def simulate_sensors():
    """Simula datos de sensores llegando cada 5 segundos."""
    phases = ["NS_GREEN", "EW_GREEN", "ALL_RED"]
    while True:
        # Actualizamos el estado global
        current_status.timestamp = datetime.utcnow().isoformat()
        current_status.vehicle_count = random.randint(50, 500)
        current_status.average_speed_kmh = round(random.uniform(10.0, 60.0), 2)
        current_status.signal_phase = random.choice(phases)

        logging.info(f"🔄 Sensor actualizado: {current_status.vehicle_count} vehículos.")

        # Dormimos 5 segundos sin bloquear el servidor (non-blocking sleep)
        await asyncio.sleep(5)


async def register_service():
    """Se registra en el Service Registry al iniciar."""
    # Esperamos un poco para asegurar que el Registry esté levantado
    await asyncio.sleep(2)
    async with httpx.AsyncClient() as client:
        try:
            # Mi propia dirección dentro de la red Docker
            my_url = f"http://{SERVICE_NAME}:{SERVICE_PORT}"
            response = await client.post(REGISTRY_URL, json={
                "service_name": SERVICE_NAME,
                "url": my_url,
                "health_url": f"{my_url}/health"
            })
            if response.status_code == 200:
                logging.info(f"✅ Registrado exitosamente en {REGISTRY_URL}")
            else:
                logging.error(f"❌ Fallo al registrar: {response.text}")
        except Exception as e:
            logging.error(f"⚠️ No se pudo conectar al Registry ({e}). ¿Está corriendo?")


# --- Ciclo de Vida de la App ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # INICIO: Arrancar tareas
    sensor_task = asyncio.create_task(simulate_sensors())
    registration_task = asyncio.create_task(register_service())
    yield
    # FIN: (Opcional) Cancelar tareas si fuera necesario
    sensor_task.cancel()


app = FastAPI(lifespan=lifespan, title="Wakanda Traffic Service")
setup_telemetry(app, SERVICE_NAME)


# --- Endpoints ---

@app.get("/traffic/status", response_model=TrafficStatus)
async def get_traffic_status():
    return current_status


@app.post("/traffic/adjust")
async def adjust_traffic(adjustment: TrafficAdjustment):
    logging.info(f"🔧 Ajustando semáforos a {adjustment.new_green_seconds}s")
    # Aquí iría la lógica real de hardware
    current_status.recommended_adjustment = adjustment
    return {"status": "adjusted", "details": adjustment}


@app.get("/health")
async def health_check():
    return {"status": "ok"}