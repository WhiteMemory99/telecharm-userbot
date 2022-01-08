"""This module contains all the official settings."""

from pyrogram import filters

from app.utils import Client, Message


@Client.on_message(filters.me & filters.command("cleanup", prefixes="."))
async def clean_up_switcher(client: Client, message: Message):
    """
    Turn on / off clean up mode that automatically deletes userbot messages
    some time after commands execution.
    This feature timings are controlled by plugin developers for the best possible UX,
    and there might be exceptions for some commands, so they will never be cleaned up.
    """
    last_value = client.user_settings.get("clean_up")
    client.user_settings.set("clean_up", not last_value)

    status = "off" if last_value else "on"
    await message.edit_text(f"Clean up is <b>{status}</b>.")


@Client.on_message(filters.me & filters.command("autofwd", prefixes="."))
async def autofwd_switcher(client: Client, message: Message):
    """
    Turn on / off auto-forwarding messages by replying to them with a dot.
    Some might notice that they are used to showing important messages to others by a dot reply.
    """
    last_value = client.user_settings.get("dot_auto_forward")
    client.user_settings.set("dot_auto_forward", not last_value)

    status = "off" if last_value else "on"
    await message.edit_text(f"Dot auto-forward is <b>{status}</b>.")
