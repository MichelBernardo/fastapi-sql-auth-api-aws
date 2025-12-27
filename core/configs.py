from typing import List, ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.declarative import declarative_base


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str

    '''
    To generate a token:
    import secrets
    token: str = secrets.token_urlsafe(32)
    '''

    JWT_SECRET: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DBBaseModel: ClassVar = declarative_base()

    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
        extra='ignore'
    )

    AWS_S3_BUCKET: str
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    # class Config:
    #     case_sensitive = True


settings = Settings()