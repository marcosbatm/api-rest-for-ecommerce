import logging
import os

from pathlib import Path


def configure_logging() -> None:
    environment = os.getenv("ENVIRONMENT", "development").lower()

    stdout_level_by_environment = {
        "development": logging.INFO,
        "testing": logging.WARNING,
        "production": logging.ERROR,
    }

    stdout_level = stdout_level_by_environment.get(environment, logging.INFO)

    logs_directory = Path(__file__).resolve().parent.parent / "logs"
    logs_directory.mkdir(parents=True, exist_ok=True)
    log_file = logs_directory / "app.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Evitar handlers duplicados (por ejemplo, en autoreload de FastAPI).
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(stdout_level)
    stdout_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stdout_handler)
