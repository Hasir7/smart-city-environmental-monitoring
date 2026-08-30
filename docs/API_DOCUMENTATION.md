# API Documentation in Basic English

## Base URLs

| Service | Local URL |
| --- | --- |
| Ingestion Service | `http://localhost:8001` |
| API Service | `http://localhost:8000` |

In Azure, both services are available through the public dashboard URL: `/ingestion` for ingestion routes and `/api` for reporting API routes.

## 1. Health Check - Ingestion

Checks if ingestion service is running.

```http
GET /health
```

Example:

```bash
curl http://localhost:8001/health
```

## 2. Submit Sensor Reading

This API accepts one IoT sensor reading and sends it to RabbitMQ.

```http
POST /readings
```

Request body:

```json
{
  "sensor_id": "sensor-air-001",
  "zone": "Bengaluru MG Road",
  "metric": "air_quality",
  "value": 105,
  "unit": "AQI"
}
```

## 3. Generate Sample Data

This API creates sample IoT readings for demo.

```http
POST /simulate?count=30
```

## 4. Health Check - API

Checks if API service is running.

```http
GET /health
```

## 5. Latest Metrics

Shows latest sensor readings.

```http
GET /metrics/latest
```

## 6. Metric Summary

Shows average, minimum, and maximum values for each metric in the last 24 hours.

```http
GET /metrics/summary
```

## 7. Zone Summary

Shows summary by city zone.

```http
GET /zones/summary
```

## 8. Alerts

Shows recent alerts.

```http
GET /alerts
```
