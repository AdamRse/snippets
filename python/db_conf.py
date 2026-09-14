import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str

    @classmethod
    def from_env(cls, env_path: str = ".env") -> "DatabaseConfig":
        """Charge le fichier .env et instancie la configuration."""
        load_dotenv(dotenv_path=env_path)

        raw_config = {
            "DB_ADDR": os.getenv("DB_ADDR"),
            "DB_PORT": os.getenv("DB_PORT"),
            "DB_NAME": os.getenv("DB_NAME"),
            "DB_USER": os.getenv("DB_USER"),
            "DB_PASSWD": os.getenv("DB_PASSWD"),
        }

        # Vérification des variables manquantes ou vides
        missing_vars = [key for key, value in raw_config.items() if not value]
        if missing_vars:
            raise ValueError(f"Variables d'environnement manquantes : {', '.join(missing_vars)}")

        try:
            port = int(raw_config["DB_PORT"])
        except ValueError:
            raise ValueError("La variable DB_PORT doit être un entier valide.")

        return cls(
            host=raw_config["DB_ADDR"],
            port=port,
            name=raw_config["DB_NAME"],
            user=raw_config["DB_USER"],
            password=raw_config["DB_PASSWD"]
        )
