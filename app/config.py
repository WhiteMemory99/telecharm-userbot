from dataclasses import dataclass
from typing import Union

from envparse import env

env.read_envfile()


@dataclass(frozen=True)
class Config:
    api_id: int
    api_hash: str
    github_url: str
    default_ttl: Union[int, float]


conf = Config(
    api_id=env.int("API_ID"),
    api_hash=env.str("API_HASH"),
    github_url="https://github.com/WhiteMemory99/telecharm-userbot",
    default_ttl=3.5,
)
