# RESTful API para Ecommerce

🇪🇸 **Español** | 🇺🇸 [English](README.en.md)

## Tabla de Contenidos

- [Contexto del Proyecto](#contexto-del-proyecto)
  - [Solución Propuesta](#solución-propuesta)
  - [Dificultades Enfrentadas](#dificultades-enfrentadas)
- [Pre-requisitos](#pre-requisitos)

## Contexto del Proyecto

Este proyecto fue desarrollado como un Entregable del Trabajo Práctico Individual (TPI) para el curso de **Ingeniería de Software II** en el marco de la carrera de *Ingeniería en Informática* de la *Universidad de Buenos Aires (UBA)*. Este trabajo fue realizado durante el primer cuatrimestre de 2026.
El objetivo fue obtener experiencia hands-on con los primeros conceptos del curso al desarrollar una API RESTful básica para una plataforma de E-Commerce.

### Solución Propuesta

Para la implementación de la API RESTful se decidió utilizar Python, más específicamente, la librería [FastAPI](https://fastapi.tiangolo.com/). La API utiliza una base de datos [PostgreSQL](https://www.postgresql.org/) para la persistencia de los datos. Ambos servicios estan orquestados mediante Docker Compose. El servicio `postgres` obtiene la imagen `postgres:16` directamente del Hub de Docker, y el servicio `api` obtiene la imagen desde el archivo [Dockerfile](Dockerfile).

### Dificultades Enfrentadas

## Pre-requisitos
