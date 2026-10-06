from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base


class Settings(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
    database=settings.DATABASE_NAME,
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()