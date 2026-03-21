import os


class Config:
    # API service configuration
    host: str
    port: str
    environment: str

    mock_db: bool

    # Database configuration
    database_host: str
    database_port: str
    database_name: str
    database_user: str
    database_password: str

    def __init__(self):
        self.host = os.getenv("HOST", "localhost")
        self.port = os.getenv("PORT", "8080")
        self.environment = os.getenv("ENVIRONMENT", "development")

        self.mock_db = os.getenv("MOCK_DB", "false").lower() == "true"

        self.database_host = os.getenv("DATABASE_HOST")
        self.database_port = os.getenv("DATABASE_PORT", "5432")
        self.database_user = os.getenv("DATABASE_USER", "postgres")
        self.database_name = os.getenv("DATABASE_NAME", self.database_user)
        self.database_password = os.getenv("DATABASE_PASSWORD")

    def is_memory_db(self) -> bool:
        return self.mock_db
