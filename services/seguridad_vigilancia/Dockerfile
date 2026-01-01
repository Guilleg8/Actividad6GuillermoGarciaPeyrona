FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wakanda_shared /app/wakanda_shared
COPY services/seguridad_vigilancia /app/services/seguridad_vigilancia
ENV PYTHONPATH=/app
ENV PORT=8005
CMD ["uvicorn", "services.seguridad_vigilancia.security_main:app", "--host", "0.0.0.0", "--port", "8005"]