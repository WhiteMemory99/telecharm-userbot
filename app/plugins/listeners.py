import asyncio

from pyrogram import filters

from app.utils import Client, Message


@Client.on_message(filters.me & filters.reply & filters.text & filters.regex(r"^[.]$"))
async def dot_auto_forwarding(client: Client, message: Message):
    """
    Listen for messages sent in reply with a dot and
    automatically forward the replied message to the current chat.
    """
    if client.user_settings.get("dot_auto_forward"):
        await asyncio.gather(
            message.reply_to_message.forward(message.chat.id, disable_notification=True),
            message.delete(),
        )
