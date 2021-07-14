from pyrogram import filters

from app import config
from app.utils import Client, Message


@Client.on_message(filters.me & filters.command("cleanup", prefixes="."))
async def clean_up_switcher(client: Client, message: Message):
    """Turn on/off cleaning up mode that deletes messages some time after editing them."""
    last_value = client.settings.get("clean_up")
    client.settings.set("clean_up", not last_value)

    status = "off" if last_value else "on"
    await message.edit_text(f"Clean up is <b>{status}</b>.", message_ttl=config.DEFAULT_TTL)


@Client.on_message(filters.me & filters.command("autofwd", prefixes="."))
async def autofwd_switcher(client: Client, message: Message):
    """Turn on/off auto-forwarding messages that are replied to with a dot."""
    last_value = client.settings.get("dot_auto_forward")
    client.settings.set("dot_auto_forward", not last_value)

    status = "off" if last_value else "on"
    await message.edit_text(f"Dot auto-forward is <b>{status}</b>.", message_ttl=config.DEFAULT_TTL)
