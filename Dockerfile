FROM python:3.12-slim
# FROM python:3.11-slim@sha256:latest

LABEL author="@marcosbatm"
LABEL description="FastAPI image"

WORKDIR /api

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY ./src /api/src

ENTRYPOINT ["fastapi", "run", "src/main.py"]
CMD ["--host", "0.0.0.0", "--port", "80"]
