# Database Design in Basic English

This project stores two main types of data.

First, it stores sensor details. This is normal structured data. Example: sensor ID, zone, metric type, and unit. This type of data fits the managed Azure Database for PostgreSQL service used by the deployed application.

Second, it stores sensor readings. This data comes continuously from IoT devices. It is time-based data because every reading has a timestamp. Azure Database for PostgreSQL keeps the capstone implementation compatible with the local PostgreSQL schema. Azure Data Explorer remains a possible future option for much larger ingestion volumes.

## Tables

| Table | Why We Need It |
| --- | --- |
| sensors | Stores basic details about each sensor |
| readings | Stores all environmental readings |
| alerts | Stores warnings when values cross safe limits |

## Why This Design Is Good

- Sensor details are stored only once.
- Readings are stored with timestamp, so latest and historical data can be queried.
- Indexes are added on metric and time for faster dashboard queries.
- Alerts are stored separately, so admin users can quickly see problems.
- This design can scale by moving readings to Azure Data Explorer later.
