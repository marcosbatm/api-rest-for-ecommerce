# RESTful API para Ecommerce

🇪🇸 **Español** | 🇺🇸 [English](README.en.md)

## Tabla de Contenidos

- [Contexto del Proyecto](#contexto-del-proyecto)
  - [Solución Propuesta](#solución-propuesta)
  - [Dificultades Enfrentadas](#dificultades-enfrentadas)
- [Pre-requisitos](#pre-requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
  - [Ejecución con Docker Compose (Recomendado)](#ejecución-con-docker-compose-recomendado)
  - [Ejecución local](#ejecución-local)
- [Variables de entorno](#variables-de-entorno)
- [Tests](#tests)

## Contexto del Proyecto

Este proyecto fue desarrollado como un Entregable del Trabajo Práctico Individual (TPI) para el curso de **Ingeniería de Software II** en el marco de la carrera de *Ingeniería en Informática* de la *Universidad de Buenos Aires (UBA)*. Este trabajo fue realizado durante el primer cuatrimestre de 2026.
El objetivo fue obtener experiencia hands-on con los primeros conceptos del curso al desarrollar una API RESTful básica para una plataforma de E-Commerce.

### Solución Propuesta

Para la implementación de la API RESTful se decidió utilizar Python, más específicamente, la librería [FastAPI](https://fastapi.tiangolo.com/). La API utiliza una base de datos [PostgreSQL](https://www.postgresql.org/) para la persistencia de los datos. Ambos servicios estan orquestados mediante Docker Compose. El servicio `postgres` obtiene la imagen `postgres:16` directamente del Hub de Docker, y el servicio `api` obtiene la imagen desde el archivo [Dockerfile](Dockerfile).

### Dificultades Enfrentadas

Esta fue mi primera vez desarrollando una API REST conectada a una base de datos, a su vez fue mi primera vez creando containers propios en Docker y utilizando Docker Compose. Por lo que la mayor dificultad que enfrenté fue la curva de aprendizaje de todas estas tecnologías que no había estudiado antes. El framework de FastAPI fue muy útil, pero también era algo completamente desconocido para mi.

Este trabajo me demandó mucho tiempo ya que tuve que aprender casi todo desde cero. Además, una de las mayores dificultades fue con las environment variables, ya que supe cómo definirlas y acceder a ellas pero no supe estructurar mi código en función de ellas.

Por ejemplo, no tenía conocimiento sobre cómo utilizar la variable `ENVIRONMENT` para adaptar mi aplicación según el caso.

## Pre-requisitos

Para levantar el entorno de desarrollo se debe tener instalado:

- **Python 3.12+**
- **pip**
- **Docker Desktop** o (**Docker Engine** + **Docker Compose**)

Todas las versiones de los paquetes y dependencias están en [requirements.txt](requirements.txt) y de allí se instalan a través del uso de virtual environments y pip.

## Instalación y ejecución

Primero. clonar el repositorio:

  ```bash
  git clone https://github.com/marcosbatm/api-rest-for-ecommerce
  cd api-rest-for-ecommerce
  ```

Luego, copiar variables de entorno de ejemplo:

  ```bash
  cp .env.example .env
  ```

Y editar `.env` según el entorno que se quiera configurar. Para más información ver [Variables de entorno](#variables-de-entorno).

El servicio `postgres` se ejecuta a través de un docker container. El servicio de la api se puede ejecutar de forma local o dentro de un Docker Compose.

### Ejecución con Docker Compose (Recomendado)

Levantar ambos servicios (`postgres` + `api`) en la misma red con Docker Compose:

  ```bash
  docker compose up -d --build
  ```

De esta forma, Docker Compose se ocupa de construir la imagen de la api y pullear la imagen de postgres. Con los servicios levantados, la API queda disponible en:

- API: `http://localhost:8080`
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

> Si en `.env` se cambió `PORT`, reemplazar `8080` por ese valor.

La API ya está disponible para interactuar con ella. Al finalizar su uso, se puede detener y remover containers con:

  ```bash
  docker compose down
  ```

> Se puede usar la opción `-v` para remover volumenes y eliminar la persistencia.

### Ejecución local

**Todos los comandos se ejecutan desde el root del repo.**

Crear el entorno virtual de python:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```
  
Nota: En Windows el venv se activa desde `venv\Scripts\activate`.

Instalar dependencias:

  ```bash
  pip install -r requirements.txt
  ```

Levantar el container de la base de datos:

Para esto debemos tener un Daemon de Docker en ejecución (a.k.a, abrir Docker Desktop). Luego levantamos el container

  ```bash
  docker compose up -d postgres
  ```

TODO: Agregar explicación para levantar la api conectandose a la bdd.

## Variables de entorno

| Variable | Requerida | Default | Valores permitidos | Descripción |
| --- | --- | ---: | --- | --- |
| `ENVIRONMENT` | No | `development` | `development`, `testing`, `production` | Entorno de ejecución |
| `MOCK_DB` | No | `false` | `true`, `false` | Mock de la database en memoria |
| `PORT` | No | `8080` | entero válido | Puerto que expone la API |
| `DATABASE_PORT` | No | `5432` | entero válido | Puerto que expone PostgreSQL(*) |
| `DATABASE_HOST` | Sí* | `postgres` | hostname/IP | Host de DB (*si `MOCK_DB=false`) |
| `DATABASE_NAME` | Sí* | - | string | Nombre de DB (*si `MOCK_DB=false`) |
| `DATABASE_USER` | Sí* | - | string | Usuario DB (*si `MOCK_DB=false`) |
| `DATABASE_PASSWORD` | Sí* | - | string | Password DB (*si `MOCK_DB=false`) |

(*) El servicio `postgres` se accede a través de `DATABASE_PORT` tanto fuera como dentro del container.

## Tests

Para correr los tests se provee de un servicio dedicado en el `compose.yaml`: `postgres_testing`. Este servicio no se levanta por defecto, se debe ejecutar `docker compose --profile test up`.

Para desarrollar los tests se utilizó [pytest](https://docs.pytest.org/en/stable/). Para correr los tests:

Primero levantar la base de datos de testing, esto lo hacemos con un Docker profile para que solo levante el servicio de testing:

  ```bash
  docker compose --profile test up -d postgres_test
  ```

Con el entorno virtual activado, corremos los tests:

  ```bash
  pytest tests/e2e -q
  ```

Al finalizar, bajamos el servicio de testing con:

  ```bash
  docker compose --profile test down -v
  ```
