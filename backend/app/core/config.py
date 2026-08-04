"""
Configuracion centralizada de la aplicacion.
Lee variables de entorno (.env) usando pydantic-settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Sistema de Horarios Universitarios"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # SQL Server (valores por defecto = docker-compose.yml del proyecto)
    DB_SERVER: str = "localhost"
    DB_PORT: int = 14330
    DB_NAME: str = "HorariosUniversitarios"
    DB_USER: str = "sa"
    DB_PASSWORD: str = "HorariosUni2026"
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_TRUST_SERVER_CERTIFICATE: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]

    # Reglas de negocio
    MAX_FILE_SIZE_MB: int = 10

    @property
    def database_url(self) -> str:
        trust = "yes" if self.DB_TRUST_SERVER_CERTIFICATE else "no"
        driver = self.DB_DRIVER.replace(" ", "+")
        return (
            f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver={driver}&TrustServerCertificate={trust}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
