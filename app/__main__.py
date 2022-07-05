import asyncio
from pathlib import Path

from aiohttp import ClientSession
from loguru import logger
from pyrogram.client import Client
from pyrogram.enums import ParseMode
from pyrogram.methods.utilities.idle import idle
from saucenaopie import AsyncSauceNao

from app import __version__
from app.config import conf
from app.storage.settings import UserSettings

try:
    import uvloop
except ImportError:
    uvloop = None
else:
    uvloop.install()


async def on_shutdown(client: Client) -> None:
    await client.stop()
    await getattr(client, "http_session").close()
    await getattr(client, "saucenao").close()
    logger.info("Telecharm v{} stopped", __version__)


async def main() -> None:
    this_dir = Path(__file__).parent
    (this_dir / "plugins" / "custom").mkdir(exist_ok=True)
    (this_dir / "files").mkdir(exist_ok=True)

    client = Client(
        this_dir.parent.name,
        api_id=conf.api_id,
        api_hash=conf.api_hash,
        plugins=dict(root="app/plugins"),
        parse_mode=ParseMode.HTML,
        workdir=(this_dir / "files").as_posix(),
    )

    if conf.saucenao_key:
        saucenao = AsyncSauceNao(conf.saucenao_key, allow_partial_success=True)
    else:
        saucenao = None

    setattr(client, "saucenao", saucenao)
    setattr(client, "http_session", ClientSession())
    setattr(client, "user_settings", UserSettings(this_dir / "files" / "user_settings.json"))

    await client.start()
    logger.info("Telecharm v{} started", __version__)

    await idle()  # Wait while the client is working
    await on_shutdown(client)


if __name__ == "__main__":
    asyncio.run(main())
