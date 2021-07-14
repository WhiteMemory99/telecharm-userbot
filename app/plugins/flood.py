import asyncio

from loguru import logger
from pyrogram import filters
from pyrogram.errors import FloodWait, RPCError

from app import config
from app.utils import quote_html, Client, Message


@Client.on_message(filters.me & filters.command("flood", prefixes="."))
async def flood_command(_, message: Message):
    """Classic flooder meant for dev purposes only. I'm not responsible for any harm or account losses."""
    args = message.get_args()
    if len(args) != 2 or not args[0].isdigit():  # Not enough arguments
        await message.edit_text(
            "Pass the number of messages and the text that will be repeated.\n\n<code>.flood 3 we are victors!</code>",
            message_ttl=config.DEFAULT_TTL
        )
    else:
        await message.delete()
        for _ in range(int(args[0])):
            try:
                await message.reply_text(quote_html(args[1]), quote=False, disable_web_page_preview=True)
            except FloodWait as ex:
                logger.error(f"Sleeping for {ex.x} seconds in .flood")
                await asyncio.sleep(ex.x)
            except RPCError as ex:
                logger.error(f"{ex} in .flood, stopping command!")
                break
