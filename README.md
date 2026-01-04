# 🏙️ Wakanda Smart City Platform

**Wakanda** es una plataforma de simulación de ciudad inteligente basada en una arquitectura de **microservicios distribuidos**. El sistema gestiona en tiempo real infraestructuras críticas como tráfico, energía, agua, residuos y seguridad, utilizando patrones de diseño avanzados para garantizar escalabilidad, resiliencia y observabilidad.

---

## 📋 Tabla de Contenidos
1. [Arquitectura del Sistema](#-arquitectura-del-sistema)
2. [Stack Tecnológico](#-stack-tecnológico)
3. [Instrucciones de Despliegue](#-instrucciones-de-despliegue)
4. [Documentación de la API (Endpoints)](#-documentación-de-la-api-endpoints)
5. [Observabilidad y Métricas](#-observabilidad-y-métricas)
6. [Resiliencia y Pruebas de Carga](#-resiliencia-y-pruebas-de-carga)
7. [Acceso a Interfaces](#-acceso-a-interfaces)

---

## 🏗 Arquitectura del Sistema

El proyecto implementa una arquitectura dirigida por **Service Discovery** y **API Gateway**.

* **Cliente (Dashboard):** Interfaz gráfica en Streamlit que interactúa exclusivamente con el Gateway.
* **API Gateway:** Punto de entrada único. Enruta dinámicamente las peticiones consultando el registro y protege el sistema con **Circuit Breakers**.
* **Service Registry:** Mantiene un catálogo en tiempo real de los servicios activos (IPs y puertos).
* **Microservicios de Dominio:** 5 servicios autónomos (Tráfico, Energía, Agua, Residuos, Seguridad) que ejecutan simulaciones en segundo plano.
* **Observabilidad:** Stack completo con Prometheus (métricas) y Jaeger (trazas distribuidas).

---

## 🛠 Stack Tecnológico

* **Lenguaje:** Python 3.9+
* **Framework Web:** FastAPI (Alto rendimiento, asíncrono).
* **Contenedores:** Docker & Docker Compose.
* **Frontend:** Streamlit.
* **Comunicación:** HTTPX (REST Asíncrono).
* **Resiliencia:** `aiobreaker` (Patrón Circuit Breaker).
* **Monitorización:**
    * **Prometheus:** Recolección de métricas.
    * **Jaeger:** Trazabilidad distribuida (Tracing).
    * **Grafana:** Visualización de datos.

---

## 🚀 Instrucciones de Despliegue

### Prerrequisitos
* Docker Engine instalado.
* Docker Compose instalado.

### Pasos para arrancar
1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/Guilleg8/Actividad6GuillermoGarciaPeyrona.git](https://github.com/Guilleg8/Actividad6GuillermoGarciaPeyrona.git)
    cd Actividad6GuillermoGarciaPeyrona
    ```

2.  **Construir y levantar los contenedores:**
    ```bash
    docker-compose up --build
    ```

3.  **Verificar estado:**
    Espera unos segundos a que todos los servicios se registren. Puedes ver los logs para confirmar:
    ```bash
    docker-compose logs -f service_registry
    ```
    *Deberías ver mensajes como: `✅ Servicio Registrado: gestion_trafico`.*

4.  **Detener el sistema:**
    ```bash
    docker-compose down
    ```

---

## 📡 Documentación de la API (Endpoints)

Todas las peticiones externas deben pasar por el **API Gateway** en el puerto `8080`.
**Formato base:** `http://localhost:8080/{nombre_servicio}/{endpoint}`

### 1. Gestión de Tráfico (`gestion_trafico`)
* `GET /traffic/status`: Obtiene el estado de la simulación (vehículos, semáforos, velocidad).
* `POST /traffic/adjust`: Ajusta la duración del semáforo manualmente.
    * *Body:* `{"intersection_id": "I-12", "duration": 45}`

### 2. Gestión de Energía (`gestion_energia`)
* `GET /energy/grid`: Estado de la red eléctrica (carga total, aporte renovable).
* `POST /energy/report`: Reporta consumo de medidores inteligentes.
    * *Body:* `{"zone_id": "Z1", "consumption_kwh": 120.5}`

### 3. Gestión de Agua (`gestion_agua`)
* `GET /water/pressure`: Lectura de sensores de presión en PSI.
* `POST /water/leak_alert`: Reporta una fuga detectada.
    * *Body:* `{"zone_id": "Norte", "severity": "HIGH"}`

### 4. Gestión de Residuos (`gestion_residuos`)
* `GET /waste/containers`: Lista de contenedores y nivel de llenado.
* `POST /waste/request_pickup`: Solicita recogida si el nivel > 70%.
    * *Body:* `{"container_id": "C-101", "fill_level_percent": 85}`

### 5. Seguridad (`seguridad_vigilancia`)
* `GET /security/events`: Historial de alertas.
* `POST /security/alert`: Emite una alerta de seguridad general.
    * *Body:* `{"location": "Plaza", "anomaly_type": "Intrusion", "description": "..."}`

---

## 📊 Observabilidad y Métricas

El sistema expone métricas en tiempo real y trazas para depuración.

### 1. Métricas Clave (Prometheus)
Accede a `http://localhost:9090` y consulta:
* `http_requests_total`: Número total de peticiones por servicio.
* `http_request_duration_seconds`: Latencia de las respuestas.
* `process_virtual_memory_bytes`: Consumo de RAM por contenedor.

### 2. Trazabilidad (Jaeger)
Accede a `http://localhost:16686`.
* Permite ver el viaje de una petición desde el **Gateway** -> **Registry** -> **Microservicio**.
* Útil para detectar cuellos de botella y timeouts.

---

## 🛡 Resiliencia y Pruebas de Carga

### Patrón Circuit Breaker
Implementado en el **Gateway** usando la librería `aiobreaker`.
* **Umbral de fallos:** 3 errores consecutivos.
* **Tiempo de recuperación:** 30 segundos.
* **Comportamiento:** Si un microservicio (ej. Tráfico) cae, el Gateway deja de enviarle peticiones inmediatamente para evitar saturación y devuelve un error 503 controlado (`Circuit Breaker Open`).

##🖥 Acceso a Interfaces
| Servicio | URL Local | Descripción |
| :--- | :--- | :--- |
| **Dashboard (Usuario)** | [http://localhost:8501](http://localhost:8501) | Panel de control visual. |
| **API Gateway** | [http://localhost:8080/docs](http://localhost:8080/docs) | Swagger UI del Gateway. |
| **Service Registry** | [http://localhost:8000/docs](http://localhost:8000/docs) | Estado del registro. |
| **Jaeger UI** | [http://localhost:16686](http://localhost:16686) | Visualización de Trazas. |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | Consultas de métricas. |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | Dashboards visuales. |
