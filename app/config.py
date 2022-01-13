from typing import Optional, Union

from pydantic import BaseSettings


class Config(BaseSettings):
    api_id: int
    api_hash: str
    saucenao_key: Optional[str] = None
    github_url: str = "https://github.com/WhiteMemory99/telecharm-userbot"
    default_ttl: Union[int, float] = 3.5

    class Config:
        allow_mutation = False
        env_file = ".env"


conf = Config()
