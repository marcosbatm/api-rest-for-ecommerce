# RESTful API for Ecommerce

🇪🇸 [Español](README.md) | 🇺🇸 **English**

## Table of Contents

- [Project Context](#project-context)
  - [Proposed Solution](#proposed-solution)
  - [Faced Difficulties](#faced-difficulties)
- [Requirements](#requirements)

## Project Context

I developed this project as a practical assignment for the **Software Engineering II** course within the *Ingeniería en Informática* degree at *Universidad de Buenos Aires (UBA)*. This work was done during the first semester of 2026.
The objective was to have a starting hands-on experience with the first concepts from the course by developing a basic Backend RESTful API project for an E-Commerce platform.

### Proposed Solution

The RESTful API is implemented in Python using [FastAPI](https://fastapi.tiangolo.com/). The API uses a [PostgreSQL](https://www.postgresql.org/) database to save the data. Both services are orquested using Docker Compose. The `postgres` service gets the image `postgres:16` directly from Dockers' Hub, and the image for the `api` service is defined in the [Dockerfile](Dockerfile).

### Faced Difficulties

## Requirements
