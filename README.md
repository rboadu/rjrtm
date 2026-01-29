Geographic API Server

A RESTful API server for managing geographic data including countries, states, and cities.
The project is designed as a production-style backend system with full CRUD support,
Swagger documentation, caching, unit tests, and cloud deployment via CI/CD.

This project serves both as a learning exercise in backend system design and as a
portfolio-quality API demonstrating best practices in API architecture.

------------------------------------------------------------
FEATURES
------------------------------------------------------------

- RESTful CRUD API
  - Countries, States, Cities
  - Bulk creation endpoints
  - Filtered queries, sorting, and pagination
- MongoDB-backed persistence
- In-memory caching
  - Read-heavy endpoints cached in RAM
  - Automatic cache invalidation on writes
- Swagger / OpenAPI documentation
- Extensive unit testing
- CI/CD-ready workflow

------------------------------------------------------------
TECH STACK
------------------------------------------------------------

Backend: Python, Flask, Flask-RESTX
Database: MongoDB
Caching: In-memory cache layer
API Docs: Swagger (Flask-RESTX)
Testing: Pytest
CI/CD: GitHub Actions (planned)
Deployment: Cloud-hosted service (planned)

------------------------------------------------------------
DATA MODEL
------------------------------------------------------------

Country:
{
  "code": "US",
  "name": "United States"
}

State:
{
  "code": "NY",
  "name": "New York",
  "country": "US"
}

City:
{
  "name": "New York City",
  "country": "US",
  "population": 8419000
}

------------------------------------------------------------
API ENDPOINTS (HIGH-LEVEL)
------------------------------------------------------------

General:
- GET  /hello
- GET  /endpoints

Countries:
- GET    /countries/
- POST   /countries/
- GET    /countries/{code}
- DELETE /countries/{code}
- GET    /countries/search?q=

States:
- GET    /states
- POST   /states
- POST   /states/bulk
- GET    /states/{code}
- PUT    /states/{code}
- PATCH  /states/{code}
- DELETE /states/{code}
- GET    /states/country/{country}

Cities:
- GET    /cities
- POST   /cities
- POST   /cities/bulk
- GET    /cities/{name}/{country}
- PUT    /cities/{name}/{country}
- DELETE /cities/{name}/{country}
- GET    /cities/{name}

------------------------------------------------------------
SWAGGER DOCUMENTATION
------------------------------------------------------------

Once the server is running, open:

http://127.0.0.1:8000/

Swagger UI provides:
- Request/response schemas
- Parameter descriptions
- Example payloads
- HTTP status codes

------------------------------------------------------------
RUNNING LOCALLY
------------------------------------------------------------

A helper script is provided:

./local.sh

This script:
- Enables Flask development mode
- Sets environment variables
- Configures PYTHONPATH
- Runs the server on port 8000

Server URL:
http://127.0.0.1:8000/

------------------------------------------------------------
TESTING
------------------------------------------------------------

All tests are run via the Makefile.

Run all tests:
make all_tests

This runs:
- API endpoint tests
- Data access layer tests
- Security tests
with coverage enabled.

------------------------------------------------------------
DEVELOPMENT ENVIRONMENT
------------------------------------------------------------

Install development dependencies:
make dev_env

Ensure PYTHONPATH is set to the project root.

------------------------------------------------------------
MAKEFILE WORKFLOW
------------------------------------------------------------

Key targets:
- make all_tests   -> run all unit tests with coverage
- make docs        -> build API documentation
- make prod        -> run tests, commit, push to GitHub

The Makefile is designed to integrate cleanly with CI/CD pipelines.
