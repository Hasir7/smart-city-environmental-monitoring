import json
import os
import time
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

import pika
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME = os.getenv("QUEUE_NAME", "sensor_readings")

app = FastAPI(title="Smart City Ingestion Service", version="1.0.0")


class SensorReading(BaseModel):
    sensor_id: str = Field(..., examples=["sensor-air-001"])
    zone: str = Field(..., examples=["Bengaluru MG Road"])
    metric: Literal["air_quality", "noise", "temperature", "humidity"]
    value: float = Field(..., examples=[72.5])
    unit: str = Field(..., examples=["AQI"])
    timestamp: datetime | None = None


def publish_message(payload: dict) -> None:
    for attempt in range(5):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            connection.close()
            return
        except pika.exceptions.AMQPConnectionError:
            time.sleep(1 + attempt)
    raise HTTPException(status_code=503, detail="Message queue is not available")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "ingestion"}


@app.post("/readings", status_code=202)
def ingest_reading(reading: SensorReading) -> dict:
    event = reading.model_dump()
    event["reading_id"] = str(uuid4())
    event["timestamp"] = (reading.timestamp or datetime.now(timezone.utc)).isoformat()
    publish_message(event)
    return {
        "message": "Reading accepted and sent to queue",
        "reading_id": event["reading_id"],
    }


@app.post("/simulate", status_code=202)
def simulate_readings(count: int = 20) -> dict:
    samples = [
        ("sensor-air-001", "Bengaluru MG Road", "air_quality", "AQI", 80),
        ("sensor-noise-002", "Chennai T Nagar", "noise", "dB", 71),
        ("sensor-temp-003", "Mumbai Andheri", "temperature", "C", 31),
        ("sensor-hum-004", "Delhi Connaught Place", "humidity", "%", 67),
    ]
    for index in range(max(1, min(count, 100))):
        sensor_id, zone, metric, unit, base_value = samples[index % len(samples)]
        event = {
            "reading_id": str(uuid4()),
            "sensor_id": sensor_id,
            "zone": zone,
            "metric": metric,
            "value": base_value + (index % 7),
            "unit": unit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        publish_message(event)
    return {"message": "Sample readings generated", "count": count}
