from typing import Union

from pydantic import BaseSettings


class Config(BaseSettings):
    api_id: int
    api_hash: str
    github_url: str = "https://github.com/WhiteMemory99/telecharm-userbot"
    default_ttl: Union[int, float] = 3.5

    class Config:
        env_file = ".env"


conf = Config()
