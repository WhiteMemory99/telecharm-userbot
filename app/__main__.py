from pathlib import Path

import pyrogram
from saucenaopie import AsyncSauceNao

from app.config import conf
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

    this_dir = Path(__file__).parent
    (this_dir / "plugins" / "custom").mkdir(exist_ok=True)
    (this_dir / "files").mkdir(exist_ok=True)

    session = pyrogram.client.FileStorage(name=this_dir.parent.name, workdir=this_dir / "files")

    Client(
        session_name=session,
        saucenao=AsyncSauceNao(conf.saucenao_key) if conf.saucenao_key else None,
        default_ttl=conf.default_ttl,
        api_id=conf.api_id,
        api_hash=conf.api_hash,
        plugins={"root": "app/plugins"},
        parse_mode="html",
    ).run()
