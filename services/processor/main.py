import json
import os
import time
from datetime import datetime, timezone
from uuid import uuid4

import pika
import psycopg


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://smartcity:smartcity@postgres:5432/smartcity",
)
QUEUE_NAME = os.getenv("QUEUE_NAME", "sensor_readings")

THRESHOLDS = {
    "air_quality": 100,
    "noise": 80,
    "temperature": 40,
    "humidity": 85,
}


def connect_database():
    for attempt in range(10):
        try:
            return psycopg.connect(DATABASE_URL)
        except psycopg.OperationalError:
            time.sleep(2 + attempt)
    raise RuntimeError("Database is not available")


def setup_database() -> None:
    with connect_database() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sensors (
                sensor_id VARCHAR(80) PRIMARY KEY,
                zone VARCHAR(120) NOT NULL,
                metric VARCHAR(40) NOT NULL,
                unit VARCHAR(20) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS readings (
                reading_id UUID PRIMARY KEY,
                sensor_id VARCHAR(80) REFERENCES sensors(sensor_id),
                zone VARCHAR(120) NOT NULL,
                metric VARCHAR(40) NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                unit VARCHAR(20) NOT NULL,
                recorded_at TIMESTAMPTZ NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id UUID PRIMARY KEY,
                sensor_id VARCHAR(80) NOT NULL,
                zone VARCHAR(120) NOT NULL,
                metric VARCHAR(40) NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                threshold DOUBLE PRECISION NOT NULL,
                severity VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_readings_metric_time ON readings(metric, recorded_at DESC);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_readings_zone_time ON readings(zone, recorded_at DESC);")
        conn.commit()


def save_reading(event: dict) -> None:
    recorded_at = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    threshold = THRESHOLDS.get(event["metric"])
    with connect_database() as conn:
        conn.execute(
            """
            INSERT INTO sensors(sensor_id, zone, metric, unit)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT(sensor_id) DO UPDATE
            SET zone = EXCLUDED.zone, metric = EXCLUDED.metric, unit = EXCLUDED.unit;
            """,
            (event["sensor_id"], event["zone"], event["metric"], event["unit"]),
        )
        conn.execute(
            """
            INSERT INTO readings(reading_id, sensor_id, zone, metric, value, unit, recorded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            (
                event["reading_id"],
                event["sensor_id"],
                event["zone"],
                event["metric"],
                event["value"],
                event["unit"],
                recorded_at,
            ),
        )
        if threshold and event["value"] >= threshold:
            conn.execute(
                """
                INSERT INTO alerts(alert_id, sensor_id, zone, metric, value, threshold, severity, message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    str(uuid4()),
                    event["sensor_id"],
                    event["zone"],
                    event["metric"],
                    event["value"],
                    threshold,
                    "high",
                    f"{event['metric']} crossed safe limit in {event['zone']}",
                ),
            )
        conn.commit()


def callback(channel, method, properties, body):
    try:
        event = json.loads(body)
        save_reading(event)
        print(f"Processed {event['reading_id']}", flush=True)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as exc:
        print(f"Processing failed: {exc}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main() -> None:
    setup_database()
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.basic_qos(prefetch_count=20)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
            print("Processor started", flush=True)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ unavailable, retrying", flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
