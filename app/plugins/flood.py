import asyncio

from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from app.utils import clean_up, get_args, quote_html


@Client.on_message(filters.me & filters.command("flood", prefixes="."))
async def flood_command(client: Client, message: Message):
    """
    Classic flooder. It's quite dangerous so use it carefully. I'm not responsible for any harm or account losses.
    """
    args = get_args(message.text or message.caption)
    if len(args) != 2 or not args[0].isdigit():  # Not enough arguments
        await message.edit_text(
            "Pass the number of messages and the text that will be repeated.\n\n<code>.flood 3 we are victors!</code>"
        )
        await clean_up(client, message.chat.id, message.message_id)
    else:
        text_to_flood = quote_html(args[1])
        await message.delete()
        for _ in range(int(args[0])):
            try:
                await message.reply_text(text_to_flood, quote=False, disable_web_page_preview=True)
            except FloodWait as ex:
                logger.error(f"Sleeping for {ex.x} seconds in .flood")
                await asyncio.sleep(ex.x)
            except RPCError as ex:
                logger.error(f"{ex} in .flood, stopping command!")
                break
