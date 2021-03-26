import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from app.storage import json_settings


@Client.on_message(filters.me & filters.reply & filters.text & filters.regex(r"^[.]$"))
async def dot_auto_forwarding(_, message: Message):
    """
    Listen for messages sent in reply with a dot and forward
    the replied message to the current chat instead of your dot reply.
    """
    if json_settings.data.get("dot_auto_forward"):
        asyncio.gather(
            message.reply_to_message.forward(message.chat.id, disable_notification=True),
            message.delete(),
        )
