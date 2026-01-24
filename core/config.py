from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Config(BaseSettings):
     drivername: str
     username: str
     password: str
     host: str
     port: int
     database: str
     echo: bool
     
     model_config = SettingsConfigDict(env_file="core/.env")
     
     def build_sqlalchemy_url(self) -> str:
          return URL.create(
               drivername="postgresql+asyncpg",
               username="postgres",
               password="193wVLAD127#!",
               host="127.0.0.1",
               port=5432,
               database="lepository"
          ).render_as_string(hide_password=False)
     
     
config = Config()