# How I Made This Project

I made this project as a distributed system for smart city environmental monitoring. First, I understood the problem. A city has many IoT sensors, and these sensors continuously send data like air quality, noise, temperature, and humidity. This data must be collected, processed, stored, and displayed in a dashboard.

After that, I designed the architecture using microservices. I created separate services for ingestion, processing, API, and frontend. This makes the system easy to understand and easy to scale. The ingestion service receives sensor data from IoT devices. Then it sends the data to RabbitMQ message queue. I used RabbitMQ because it helps the system handle high traffic safely.

Next, I created the processor service. This service reads messages from RabbitMQ, stores the readings in the database, and creates alerts when values cross safe limits. For example, if air quality becomes too high, the system creates an alert for city administrators.

Then I created the API service using FastAPI. This API gives latest readings, metric summaries, zone summaries, and alerts to the frontend. I created a React dashboard to show this data in a simple visual way.

For local running, I used Docker Compose. It starts RabbitMQ, PostgreSQL, ingestion service, processor service, API service, and frontend together. For cloud deployment, I added Kubernetes manifests for AKS, Terraform for AKS, ACR, Azure Database for PostgreSQL, and Key Vault, plus an Azure DevOps pipeline. The public frontend proxies requests to the internal API and ingestion services.

Finally, I added documentation for architecture, database design, best practices, deployment, security, monitoring, and cost management. This project helped me understand microservices, message queues, stream processing, Docker, Kubernetes, Terraform, CI/CD, and cloud monitoring in a practical way.
