"""This module contains all the official settings."""

from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.me & filters.command("autofwd", prefixes="."))
async def autofwd_switcher(client: Client, message: Message) -> None:
    """
    Turn on / off auto-forwarding messages by replying to them with a dot.
    Some might notice that they are used to showing important messages to others by a dot reply.
    """
    settings = getattr(client, "user_settings")
    last_value = settings.get("dot_auto_forward")
    settings.set("dot_auto_forward", not last_value)

    status = "off" if last_value else "on"
    await message.edit_text(f"Dot auto-forward is <b>{status}</b>.")
