from typing import List, ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.declarative import declarative_base


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str

    JWT_SECRET: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DBBaseModel: ClassVar = declarative_base()

    AWS_S3_BUCKET: str
    AWS_REGION: str

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra='ignore'
    )


settings = Settings()