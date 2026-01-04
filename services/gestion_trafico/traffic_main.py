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

class TrafficUpdate(BaseModel):
    intersection_id: str   # <--- ¡ESTE ES EL NOMBRE QUE BUSCAMOS!
    duration: int          # <--- ¡Y ESTE!

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
# ... (Tu código anterior iría aquí arriba) ...

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)

# --- Variables Globales de Control ---
SIMULATION_RUNNING = False
CURRENT_GREEN_DURATION = 30  # Duración por defecto


# --- Lógica de Negocio: Simulación de Tráfico ---
async def simulate_traffic_cycle():
    """
    Simula cambios en el tráfico y el estado del semáforo en segundo plano.
    Actualiza la variable global `current_status`.
    """
    global current_status
    phases = ["RED", "GREEN", "YELLOW"]

    while SIMULATION_RUNNING:
        # Simular datos aleatorios
        vehicle_count = random.randint(0, 50)

        # A más coches, menor velocidad promedio (lógica simple)
        speed = max(5.0, 60.0 - vehicle_count * 0.8) if vehicle_count > 0 else 0.0

        # Cambiar fase del semáforo aleatoriamente para la demo
        current_phase = random.choice(phases)

        # Actualizar el estado global
        current_status = TrafficStatus(
            intersection_id="I-12",
            timestamp=datetime.utcnow().isoformat(),
            vehicle_count=vehicle_count,
            average_speed_kmh=round(speed, 2),
            signal_phase=current_phase,
            recommended_adjustment=TrafficAdjustment(new_green_seconds=CURRENT_GREEN_DURATION)
        )

        logger.debug(f"Simulación actualizada: {vehicle_count} vehículos, Fase {current_phase}")
        await asyncio.sleep(3)  # Actualiza cada 3 segundos


# --- Lógica de Infraestructura: Registro de Servicio ---
async def register_service():
    """Intenta registrar este servicio en el Service Registry."""
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "name": SERVICE_NAME,
                "url": f"http://gestion_trafico:{SERVICE_PORT}",  # Hostname de Docker
                "health_endpoint": f"http://gestion_trafico:{SERVICE_PORT}/health"
            }
            response = await client.post(REGISTRY_URL, json=payload, timeout=5.0)
            if response.status_code in [200, 201]:
                logger.info(f"✅ Servicio registrado exitosamente en {REGISTRY_URL}")
            else:
                logger.warning(f"⚠️ Fallo al registrar servicio: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ No se pudo contactar con el registry: {e}")


# --- Lifespan (Ciclo de Vida) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Inicio: Configurar telemetría y simulación
    setup_telemetry(app, SERVICE_NAME)

    global SIMULATION_RUNNING
    SIMULATION_RUNNING = True
    simulation_task = asyncio.create_task(simulate_traffic_cycle())

    # 2. Inicio: Intentar registrar el servicio
    # Usamos create_task para no bloquear el arranque si el registry está lento
    asyncio.create_task(register_service())

    yield  # El servicio corre aquí

    # 3. Apagado: Limpieza
    SIMULATION_RUNNING = False
    simulation_task.cancel()
    logger.info("🛑 Servicio detenido")


# --- Instancia de FastAPI ---
app = FastAPI(
    title="Servicio de Gestión de Tráfico",
    lifespan=lifespan
)


# --- Endpoints ---

@app.get("/health")
async def health_check():
    """Endpoint estándar de salud para Docker/K8s."""
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/status", response_model=TrafficStatus)
async def get_traffic_status():
    """Devuelve el estado actual (simulado) de la intersección."""
    return current_status


@app.post("/adjust_signal")
async def adjust_traffic_signal(update: TrafficUpdate):
    """
    Recibe actualizaciones externas para modificar el semáforo.
    Aquí usamos el modelo TrafficUpdate que definiste.
    """
    global CURRENT_GREEN_DURATION

    logger.info(f"📡 Recibida solicitud de ajuste para intersección {update.intersection_id}")
    logger.info(f"⏱️ Ajustando duración de luz verde a {update.duration} segundos")

    # Actualizamos la variable que usa la simulación
    CURRENT_GREEN_DURATION = update.duration

    return {
        "status": "success",
        "message": f"Duración actualizada a {update.duration}s para intersección {update.intersection_id}"
    }


# --- Entrypoint para ejecución local ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)