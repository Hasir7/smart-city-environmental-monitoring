import os
from contextlib import contextmanager

import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://smartcity:smartcity@postgres:5432/smartcity",
)

app = FastAPI(title="Smart City API Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def get_conn():
    with psycopg.connect(DATABASE_URL, row_factory=psycopg.rows.dict_row) as conn:
        yield conn


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "api"}


@app.get("/metrics/latest")
def latest_metrics(limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT reading_id, sensor_id, zone, metric, value, unit, recorded_at
            FROM readings
            ORDER BY recorded_at DESC
            LIMIT %s;
            """,
            (min(limit, 100),),
        ).fetchall()
    return rows


@app.get("/metrics/summary")
def summary() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                metric,
                COUNT(*) AS total_readings,
                ROUND(AVG(value)::numeric, 2) AS average_value,
                ROUND(MAX(value)::numeric, 2) AS max_value,
                ROUND(MIN(value)::numeric, 2) AS min_value
            FROM readings
            WHERE recorded_at >= NOW() - INTERVAL '24 hours'
            GROUP BY metric
            ORDER BY metric;
            """
        ).fetchall()
    return rows


@app.get("/zones/summary")
def zone_summary() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                zone,
                COUNT(*) AS total_readings,
                ROUND(AVG(value)::numeric, 2) AS average_value
            FROM readings
            WHERE recorded_at >= NOW() - INTERVAL '24 hours'
            GROUP BY zone
            ORDER BY zone;
            """
        ).fetchall()
    return rows


@app.get("/alerts")
def alerts(limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT alert_id, sensor_id, zone, metric, value, threshold, severity, message, created_at
            FROM alerts
            ORDER BY created_at DESC
            LIMIT %s;
            """,
            (min(limit, 100),),
        ).fetchall()
    return rows
