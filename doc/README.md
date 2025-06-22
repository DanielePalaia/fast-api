# Fever Events API

## Introduction

This project implements a microservice to integrate and expose event data from an external provider into the Fever marketplace. It fetches events in XML format from the provider, stores them in a PostgreSQL database, and exposes a performant API endpoint to query events based on time ranges.

### Tech stack
- **Python 3.10+**
- **Poetry** — For dependency management and packaging
- **FastAPI** — Web framework for building the API natively supporting async operations
- **uvicorn** - An ASGI web server 
- **SQLAlchemy** — ORM for interacting with PostgreSQL (or another DBMS)
- **PostgreSQL** — Relational database for event storage chosen for the example
- **HTTPX** — Async HTTP client for fetching external provider data
- **Docker** — Containerization for easy deployment

---

## Getting Started

### Prerequisites

- Docker (at minimum)
- Poetry installed (optional for local development)
- PostgreSQL instance running (can be Dockerized)

### Installation & Run

1. Run postgresql via docker:
    ```bash
    make start-db
    ```

2. Run the microservice via docker
    ```bash
    make build-docker
    make run-docker
    ```

3. Run locally (optional)
    .env parameters
    ```
    PROVIDER_URL=https://provider.code-challenge.feverup.com/api/events
    DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/feverdb
    REFRESH_TIMEOUT=300  # Sync interval in seconds
    ```

    then:
    ```
    make install
    make run
    ```
    
4. The API will be accessible at: `http://localhost:8000`

5. Swagger UI docs at: `http://localhost:8000/docs`

---

## Design Overview

The project is composed in different modules:
  - models.py: ORM definition model
  - session.py: Database session management
  - client.py: External data fetching and XML parsing.
  - endpoints.py:  API definition.
  - sync.py: Background data sync logic with the database ingestion
  - tests are provided in the tests folder

- **Data Sync**  
  - Background task periodically fetches event data from the external provider.
  - Plans are parsed from XML and stored in the database if ever sell_mode is online
  - Uses UPSERT logic to update existing events or insert new ones.

- **API Endpoint**  
  - `/events` endpoint accepts `starts_at` and `ends_at` query parameters.
  - Returns all events with `"sell_mode": "online"` in the given time range.
  - Past events remain queryable even if no longer available from the provider.

- **Database**  
  - PostgreSQL stores event data.
  - Indexes added on `start_date`, and `end_date` for fast queries.
  - Composite index optimizes the main query filter.

- **Error Handling & Resilience**  
  - API responds independently of external provider availability.
  - Sync failures are logged but do not impact API responsiveness.
 
  Prices are aggreagated for every zone in a plan during inserction in the database and aggregated again for every plan in the event during api querying
---

## Scalability/Availability Considerations

- **Improve database performance**
  - Better tuning of the database (indexes, partitioning, internal database cache and if possible a sharding solution - in the worst case to consider MongoDB or another document database)
  - Enable Postgresql read replicas to allow at least parallelization on reading and failover

- **Horizontal scaling**  
  - Multiple API instances can be deployed in different hosts behind a load balancer or better in Kubernetes or another container orchestrator
  - Shared PostgreSQL database accessed by all instances or eventually MongoDB for better scalability (supports sharding natively)
  - If the main database (Postgresql or even MongoDB) become a bottleneck put an in-memory database like Redis in front of it
 
- **Availability**
  - Run multiple instances of the services in Kubernetes (or another container orchestrator), setting up a Deployment and a LoadBalancer, better if nodes of the K8s cluster are
      located in different availability zones/geographical regions
  - Enable Postgresql read replicas to allow failover     

---

## Possible Improvements

- **Pagination**  
  - Not implemented for lack of time

- **Integration with Prometheus**  
  - Some metrics can be exported for monitoring to Prometheus like: total number of HTTP requests, Request processing time (latency), Current number of in-flight requests ecc ecc...

- **Integration with OpenTelemetry**  
  - There are always more and more interests and requests from the community on microservices to monitor tracings

- **Add a github action**  
  - That run at least isort, black, flake8 and mypy and the unit tests on every PR and in main like: https://github.com/rabbitmq-community/rstream/blob/master/.github/workflows/test.yaml
 
- **Rate limiting & throttling**  
  - Protect the API from abuse and spikes.

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Contact

Created by Daniele — daniele985@gmail.com

