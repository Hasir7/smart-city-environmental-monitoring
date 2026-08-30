# 12 Minute Video Walkthrough Script

## 1. Introduction

Hello, my name is Mohamed Hasir. In this video, I am explaining my capstone project, Smart City Environmental Monitoring Platform.

This is a distributed system. It collects real-time environmental data from IoT sensors in a city. The system monitors air quality, noise, temperature, and humidity. The main users are city administrators and monitoring teams.

The project uses microservices, RabbitMQ message queue, PostgreSQL for local demo, React dashboard, Docker, Kubernetes, Azure DevOps pipeline, Terraform, Azure Key Vault, and Azure Monitor.

## 2. Problem and Requirements

The problem is that city environmental data changes every minute. If this data is checked manually, it is slow and not useful for real-time decisions.

So this system collects data automatically from IoT devices. The functional requirements are data ingestion, message queue, stream processing, database storage, REST API, dashboard, and alerts.

The non-functional requirements are scalability, availability, fault tolerance, low latency, security, monitoring, and cost control.

Distributed architecture is needed because many sensors can send data at the same time. One single application may become slow. Microservices help us scale each part separately.

## 3. High-Level Architecture

The data flow is simple:

IoT Sensors send data to the Ingestion Service. The Ingestion Service sends messages to RabbitMQ. The Processor Service reads messages from RabbitMQ, stores data in the database, and creates alerts. The API Service reads the database and gives data to the frontend dashboard. The React dashboard shows latest readings, charts, and alerts.

This design is modular. If ingestion traffic increases, we can scale only the ingestion service. If processing becomes slow, we can scale processor replicas.

## 4. Messaging and Real-Time Processing

RabbitMQ is used as the message queue. A queue is useful because it separates the sender and receiver.

If many IoT sensors send data at the same time, RabbitMQ stores the messages. The processor service can process messages safely. If the processor is temporarily down, messages can wait in the queue.

The processor does three jobs. First, it stores sensor metadata. Second, it stores the reading. Third, it checks if the value crossed the safe limit. For example, if air quality goes above 100 AQI, the system creates an alert.

## 5. Database Design

The project has three main tables: sensors, readings, and alerts.

The sensors table stores sensor ID, zone, metric, and unit. This is structured data, so relational database is good.

The readings table stores all sensor values with timestamp. This is time-series style data. In a full Azure system, Azure Data Explorer can be used for very large sensor data. For this local working demo, PostgreSQL is used.

The alerts table stores dangerous readings separately so administrators can quickly see problems.

Indexes are added on metric, zone, and time. This helps dashboard queries run faster.

## 6. Deployment, Docker, and CI/CD

All services are Dockerized. This means each service has its own Dockerfile and can run in a container.

For local demo, Docker Compose starts RabbitMQ, PostgreSQL, ingestion service, processor service, API service, and frontend.

For cloud deployment, Kubernetes manifests are provided for AKS. The project includes deployments, services, Key Vault CSI secret synchronization, config maps, and a horizontal pod autoscaler. Azure Database for PostgreSQL stores deployed data, and one load balancer exposes the public dashboard.

The Azure DevOps pipeline builds versioned Docker images, pushes them to Azure Container Registry, renders deployment placeholders, and deploys the manifests to AKS.

## 7. Security, Monitoring, and Reliability

For security, production secrets should be stored in Azure Key Vault. Kubernetes Secrets are used in the demo files. RBAC should be enabled in Kubernetes so only allowed users can access resources.

For monitoring, Azure Monitor, Application Insights, and Log Analytics are used. They can monitor logs, errors, latency, CPU, memory, and pod restarts.

The system is reliable because RabbitMQ helps prevent data loss. Kubernetes can restart failed containers. Multiple replicas can improve availability.

## 8. Scalability and Trade-Offs

This system scales horizontally. That means we can add more service replicas when traffic increases.

The main trade-off is cost versus performance. More replicas improve performance, but they increase cloud cost. Another trade-off is consistency versus availability. For real-time monitoring, the system should be highly available, but database consistency is still important for alerts.

Future improvements can include login authentication, map view, Azure Data Explorer integration, caching, anomaly detection using machine learning, and SMS or email alert notification.

## 9. Demo Flow

First, I run Docker Compose. Then I open the frontend dashboard. I generate sample IoT data using the button or API endpoint. After that, I show the latest readings table, metric summary chart, and alerts.

Then I explain the API docs, Docker files, Kubernetes files, Terraform files, and Azure pipeline YAML.

This completes the project walkthrough. Thank you.
