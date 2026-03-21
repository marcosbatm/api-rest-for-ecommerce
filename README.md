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
- [Documentación de la API](#documentación-de-la-api)
- [Desafios](#desafios)
  - [Mejoras a la Solución](#mejoras-a-la-solución)
  - [Uso de Docker Compose](#uso-de-docker-compose)
  - [CI/CD con Github Actions para tests](#cicd-con-github-actions-para-tests)

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

> Nota: Para levantar la API en local, levantar solo el servicio de postgres con:

  ```bash
  docker compose up -d postgres
  ```

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

Luego, para ejecutar la API localmente se recomienda `fastapi dev` (modo desarrollo: recarga automática y logs más detallados); en cambio `fastapi run` es para ejecución más estable tipo producción (sin autoreload). Primero declarar las variables de entorno (`ENVIRONMENT`, `HOST`, `PORT` y `DATABASE_*`), siendo `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER` y `DATABASE_PASSWORD` obligatorias, y después correr todo en un solo comando (como la API corre fuera de Docker, usar `DATABASE_HOST=localhost`; si corre dentro de Compose, usar `DATABASE_HOST=postgres`, el resto deben ser iguales a las de `.env`).

Por ejemplo:

  ```bash
  ENVIRONMENT=development \
  HOST=localhost \
  PORT=8080 \
  DATABASE_HOST=localhost \
  DATABASE_PORT=5432 \
  DATABASE_NAME=ecommerce_db \
  DATABASE_USER=myuser \
  DATABASE_PASSWORD=mypassword \
  fastapi dev src/main.py --host localhost --PORT 8080
  ```

Otra alternativa es exportar las environment variables directamente desde `.env`, lo que permite ejecutar:

  ```bash
  set -a
  source .env
  set +a
  fastapi dev src/main.py --host $HOST --port $PORT
  ```

## Variables de entorno

| Variable | Requerida | Default | Valores permitidos | Descripción |
| --- | --- | ---: | --- | --- |
| `ENVIRONMENT` | No | `development` | `development`, `testing`, `production` | Entorno de ejecución |
| `MOCK_DB` | No | `false` | `true`, `false` | Mock de la database en memoria |
| `HOST` | No | `0.0.0.0` | valores de host | Host en el que exponer la API |
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

Primero levantar la base de datos de testing:

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

## Documentación de la API

Al utilizar FastAPI, la misma provee documentación OpenAPI generada automáticamente. La misma se puede acceder en el path `/docs` de la App. La API se implementó buscando replicar la especificación OpenAPI provista por la cátedra.

## Desafios

A continuación se detalla los desafíos opcionales realizados:

1. Usar Middleware para Manejar Errores: NO
2. Mejoras a la Solución: SI
3. Uso de Docker Compose: SI
4. CI/CD con GitHub Actions para tests: SI

### Mejoras a la Solución

La solución no es perfecta. Algunas mejoras posibles y pendientes son:

- Mejor manejo manejo de errores: Ya que en algunos casos, simplemente se atrapa el error automático de FastAPI (422) y se pone directamente en el campo `"detail"` de las ErrorResponse. Un mejor manejo de errores tendría mensajes detail más personalizados y formateados.
- Se implementó dos tipos de capas Repository, una Memory y una Database. Para ello se utilizó polimorfismo y herencia, pero algunas partes del código se podrían refactorizar para obtener código de mayor calidad.
- Faltó documentar con docstrings claras y extensas todas las funciones y clases definidas.
- Los modelos que utiliza la app (`src/models/`) se usan como structs en lugar de clases. Se podría aplicar encapsulamiento exponiendo métodos o en su defecto definirlos como `@dataclass`.
- Mejorar la separación en responsabilidades: algunos métodos de la capa Repository y/o Router se ocupan de realizar algunas verificaciones que podrían corresponder a servicio (o al menos debería haber mayor consistencia al respecto). Esto se correlaciona con el primer punto de manejo de errores (un Middleware podría resolver esto).

### Uso de Docker Compose

Como se vió [previamente](#ejecución-con-docker-compose-recomendado), se implementó un [compose](compose.yaml) file para levantar ambos servicios de forma aislada.

### CI/CD con GitHub Actions para tests

Se implementó un workflow [tests.yml](.github/workflows/tests.yml) que ejecuta los tests de forma automática ante cualquier push o pull request en `main`. El mismo corre en `ubuntu-latest`, clona el repositorio, configura Python, levanta el servicio de `postgres_testing` en Docker y luego corre los tests con las variables de entorno en `.env.example`.
