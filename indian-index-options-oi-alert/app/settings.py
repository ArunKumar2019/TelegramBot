import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    config_path: Path
    data_dir: Path
    mock_mode: bool
    refresh_interval_minutes: int
    tracked_strikes_each_side: int
    default_cooldown_minutes: int
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str


def load_settings() -> Settings:
    load_dotenv(PROJECT_ROOT / ".env")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "oi_alert_app")
    db_password = os.getenv("DB_PASSWORD", "Arun@123")
    db_name = os.getenv("DB_NAME", "oi_alert")
    config_path = Path(
        os.getenv("CONFIG_PATH", PROJECT_ROOT / "config.yaml")
    )
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    config: dict = {}
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

    bot_config = config.get("bot", {})
    market_config = config.get("market", {})
    alert_config = config.get("alerts", {})

    data_dir = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir

    settings = Settings(

        config_path=config_path,
        data_dir=data_dir,
        mock_mode=os.getenv(
            "MOCK_MODE",
            str(bot_config.get("mock_mode", True)),
        ).lower() in {"1", "true", "yes", "on"},
        refresh_interval_minutes=int(
            os.getenv(
                "REFRESH_INTERVAL_MINUTES",
                market_config.get("refresh_interval_minutes", 1),
            )
        ),
        tracked_strikes_each_side=int(
            os.getenv(
                "TRACKED_STRIKES_EACH_SIDE",
                market_config.get("tracked_strikes_each_side", 5),
            )
        ),
        default_cooldown_minutes=int(
            os.getenv(
                "DEFAULT_COOLDOWN_MINUTES",
                alert_config.get("default_cooldown_minutes", 20),
            )
        ),
        db_host=db_host,
        db_port=db_port,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
    )

    if not 1 <= settings.refresh_interval_minutes <= 5:
        raise ValueError("Refresh interval must be between 1 and 5 minutes.")
    if settings.tracked_strikes_each_side < 1:
        raise ValueError("Tracked strike count must be at least 1.")
    if settings.default_cooldown_minutes < 0:
        raise ValueError("Cooldown cannot be negative.")

    return settings