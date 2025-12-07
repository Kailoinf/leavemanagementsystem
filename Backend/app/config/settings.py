import logging
import toml
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings:
    def __init__(self, config_file: str = "config.toml"):
        self.config_file = Path(config_file)
        self._config_data = None
        self._load_config()

    def _load_config(self):
        try:
            self._config_data = toml.load(self.config_file)
        except FileNotFoundError:
            logger.error("❌ config.toml not found")
            raise RuntimeError("Database config missing")
        except toml.TomlDecodeError as e:
            logger.error(f"❌ Invalid TOML: {e}")
            raise RuntimeError("Database config corrupted")

    @property
    def database_url(self) -> str:
        db_path = self._config_data["database"]["path"]
        return f"sqlite:///{db_path}"

    @property
    def database_path(self) -> str:
        return self._config_data["database"]["path"]


settings = Settings()