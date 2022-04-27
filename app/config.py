from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    api_id: int
    api_hash: str
    saucenao_key: Optional[str] = None
    github_url: str = "https://github.com/WhiteMemory99/telecharm-userbot"

    class Config:
        allow_mutation = False


conf = Config()
