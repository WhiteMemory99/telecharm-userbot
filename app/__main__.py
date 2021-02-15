from pathlib import Path

from pyrogram import Client

from app import config

try:
    import uvloop
except ImportError:
    uvloop = None
else:
    uvloop.install()

if __name__ == "__main__":
    Client(
        session_name=Path(__file__).parent.name,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        plugins={"root": "app/plugins"},
        parse_mode="html",
    ).run()
