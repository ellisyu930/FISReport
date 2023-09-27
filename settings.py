from pydantic import EmailStr, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict
import os
from functools import lru_cache


class GlobalSettings(BaseSettings, case_sensitive=True):
    model_config = SettingsConfigDict(extra="ignore")

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: SecretStr
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    RECIPIENTS: List[EmailStr]
    SCHEDULER_TIMEZONE: str
    SCHEDULER_TYPE: str
    SCHEDULER_HOUR: int
    SCHEDULER_MINUTE: int
    SCHEDULER_INT_HOURS: int
    SCHEDULER_INT_MINUTES: int
    MISFIRE_GRACE_TIME: int
    PREV_TIME_FILENAME: str
    FIS_BASE_URL: str
    RPT_DATE_FORMAT: str
    FIS_FILENAME_PREFIX: Dict


class DevSettings(GlobalSettings):
    model_config = SettingsConfigDict(env_file="./env/.env.testing")


class ProdSettings(GlobalSettings):
    model_config = SettingsConfigDict(env_file="./env/.env")


@lru_cache()
def get_settings() -> ProdSettings | DevSettings | None:
    try:
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            config = ProdSettings()
        else:
            config = DevSettings()
        print(config)
        return config
    except ValidationError as e:
        print(e)
