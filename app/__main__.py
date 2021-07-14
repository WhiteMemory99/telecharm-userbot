import pyrogram
from pathlib import Path

from app import config
from app.utils.types import Client, Message

try:
    import uvloop
except ImportError:
    uvloop = None
else:
    uvloop.install()

if __name__ == "__main__":
    # Please, god, forgive me.
    for name, func in Message.__dict__.items():
        setattr(pyrogram.types.Message, name, func)

    Client(
        session_name=Path(__file__).parent.name,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        plugins={"root": "app/plugins"},
        parse_mode="html",
    ).run()
