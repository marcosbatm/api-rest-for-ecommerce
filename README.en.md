# RESTful API for Ecommerce

🇪🇸 [Español](README.md) | 🇺🇸 **English**

## Table of Contents

- [Project Context](#project-context)
  - [Proposed Solution](#proposed-solution)
  - [Faced Difficulties](#faced-difficulties)
- [Prerequisites](#prerequisites)
- [Installation and Run](#installation-and-run)
  - [Run with Docker Compose (Recommended)](#run-with-docker-compose-recommended)
  - [Run Locally](#run-locally)
- [Environment Variables](#environment-variables)
- [Tests](#tests)
- [API Documentation](#api-documentation)
- [Challenges](#challenges)
  - [Solution Improvements](#solution-improvements)
  - [Using Docker Compose](#using-docker-compose)
  - [CI/CD with GitHub Actions for Tests](#cicd-with-github-actions-for-tests)

## Project Context

This project was developed as a deliverable for an individual practical assignment in the **Software Engineering II** course, within the *Computer Engineering* degree at the *University of Buenos Aires (UBA)*. This work was completed during the first semester of 2026.
The objective was to gain hands-on experience with the first course concepts by developing a basic RESTful API for an E-Commerce platform.

### Proposed Solution

To implement the RESTful API, Python was chosen, specifically the [FastAPI](https://fastapi.tiangolo.com/) framework. The API uses a [PostgreSQL](https://www.postgresql.org/) database for data persistence. Both services are orchestrated with Docker Compose. The `postgres` service uses the `postgres:16` image directly from Docker Hub, and the `api` service image is built from the [Dockerfile](Dockerfile).

### Faced Difficulties

This was my first time developing a REST API connected to a database, and also my first time creating custom Docker containers and using Docker Compose. So the biggest challenge was the learning curve of all these technologies I had not studied before. FastAPI was very useful, but it was also completely new to me.

This assignment took me a lot of time because I had to learn almost everything from scratch. In addition, one of the biggest challenges was environment variables: I learned how to define and read them, but I did not know how to structure my code around them.

For example, I did not initially know how to use the `ENVIRONMENT` variable to adapt the application behavior depending on the case.

## Prerequisites

To run the development environment, you need:

- **Python 3.12+**
- **pip**
- **Docker Desktop** or (**Docker Engine** + **Docker Compose**)

All package and dependency versions are listed in [requirements.txt](requirements.txt), and they are installed using virtual environments and pip.

## Installation and Run

First, clone the repository:

  ```bash
  git clone https://github.com/marcosbatm/api-rest-for-ecommerce
  cd api-rest-for-ecommerce
  ```

Then copy the example environment variables:

  ```bash
  cp .env.example .env
  ```

And edit `.env` according to the target environment. For more information, see [Environment Variables](#environment-variables).

The `postgres` service runs in a Docker container. The API service can run either locally or inside Docker Compose.

### Run with Docker Compose (Recommended)

Start both services (`postgres` + `api`) in the same network with Docker Compose:

  ```bash
  docker compose up -d --build
  ```

Docker Compose will build the API image and pull the PostgreSQL image. Once services are running, the API is available at:

- API: `http://localhost:8080`
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

> If `PORT` was changed in `.env`, replace `8080` with that value.

The API is ready to use. When finished, stop and remove containers with:

  ```bash
  docker compose down
  ```

> You can add `-v` to remove volumes and delete persisted data.

### Run Locally

**All commands must be executed from the repository root.**

> Note: to run the API locally, start only the PostgreSQL service with:

  ```bash
  docker compose up -d postgres
  ```

Create the Python virtual environment:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

Note: on Windows, activate it with `venv\Scripts\activate`.

Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

Then, to run the API locally, `fastapi dev` is recommended (development mode: auto-reload and more detailed logs); `fastapi run` is for more stable production-like execution (without auto-reload). First declare environment variables (`ENVIRONMENT`, `HOST`, `PORT`, and `DATABASE_*`), where `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, and `DATABASE_PASSWORD` are mandatory, then run everything in a single command (since the API runs outside Docker, use `DATABASE_HOST=localhost`; if it runs inside Compose, use `DATABASE_HOST=postgres`; the rest must match `.env`).

For example:

  ```bash
  ENVIRONMENT=development \
  HOST=localhost \
  PORT=8080 \
  DATABASE_HOST=localhost \
  DATABASE_PORT=5432 \
  DATABASE_NAME=ecommerce_db \
  DATABASE_USER=myuser \
  DATABASE_PASSWORD=mypassword \
  fastapi dev src/main.py --host localhost --port 8080
  ```

Another option is exporting environment variables directly from `.env`, which allows running:

  ```bash
  set -a
  source .env
  set +a
  fastapi dev src/main.py --host $HOST --port $PORT
  ```

## Environment Variables

| Variable | Required | Default | Allowed values | Description |
| --- | --- | ---: | --- | --- |
| `ENVIRONMENT` | No | `development` | `development`, `testing`, `production` | Runtime environment |
| `MOCK_DB` | No | `false` | `true`, `false` | In-memory database mock |
| `HOST` | No | `0.0.0.0` | host values | Host where the API is exposed |
| `PORT` | No | `8080` | valid integer | API exposed port |
| `DATABASE_PORT` | No | `5432` | valid integer | PostgreSQL exposed port (*) |
| `DATABASE_HOST` | Yes* | `postgres` | hostname/IP | DB host (*if `MOCK_DB=false`) |
| `DATABASE_NAME` | Yes* | - | string | DB name (*if `MOCK_DB=false`) |
| `DATABASE_USER` | Yes* | - | string | DB user (*if `MOCK_DB=false`) |
| `DATABASE_PASSWORD` | Yes* | - | string | DB password (*if `MOCK_DB=false`) |

(*) The `postgres` service is accessed through `DATABASE_PORT` both outside and inside the container.

## Tests

To run tests, a dedicated service is provided in `compose.yaml`: `postgres_testing`. This service is not started by default; run `docker compose --profile test up`.

Tests were developed with [pytest](https://docs.pytest.org/en/stable/). To run tests:

First, start the testing database:

  ```bash
  docker compose --profile test up -d postgres_testing
  ```

With the virtual environment activated, run tests:

  ```bash
  pytest tests/e2e -q
  ```

When finished, stop the testing service with:

  ```bash
  docker compose --profile test down -v
  ```

## API Documentation

Since FastAPI is used, it provides automatically generated OpenAPI documentation. It is available at the `/docs` path of the app. The API was implemented to replicate the OpenAPI specification provided by the course.

## Challenges

The optional challenges completed are listed below:

1. Use Middleware to Handle Errors: NO
2. Solution Improvements: YES
3. Using Docker Compose: YES
4. CI/CD with GitHub Actions for tests: YES

### Solution Improvements

The solution is not perfect. Some possible and pending improvements are:

- Better error handling: in some cases, the automatic FastAPI error (422) is simply caught and put directly into the `"detail"` field of `ErrorResponse`. Better error handling would provide more customized and formatted `detail` messages.
- Two repository implementations were built (Memory and Database). This uses polymorphism and inheritance, but some parts could be refactored for better code quality.
- It is still pending to add clear and extensive docstrings to all defined functions and classes.
- The app models (`src/models/`) are used as structs instead of classes. Encapsulation could be applied by exposing methods, or alternatively defining them as `@dataclass`.
- Improve separation of responsibilities: some methods in the Repository and/or Router layers perform validations that may belong in the service layer (or at least there should be more consistency). This is related to the first point about error handling (a Middleware could help solve this).

### Using Docker Compose

As shown [above](#run-with-docker-compose-recommended), a [compose](compose.yaml) file was implemented to start both services in an isolated setup.

### CI/CD with GitHub Actions for Tests

A workflow [tests.yml](.github/workflows/tests.yml) was implemented to run tests automatically on every push or pull request to `main`. It runs on `ubuntu-latest`, checks out the repository, configures Python, starts the `postgres_testing` Docker service, and then runs tests with environment variables from `.env.example`.
