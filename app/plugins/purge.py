from typing import List

from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message

from app.utils import get_args


@Client.on_message(filters.me & filters.reply & filters.command("purge", prefixes="."))
async def purge_command(client: Client, message: Message):
    """
    Purge messages in any chat, supports 2 working modes: my messages and all messages.
    """
    args = get_args(message.text or message.caption)
    me_mode = "me" in args

    if message.chat.type in ("group", "supergroup") and not me_mode:  # Check admin rights if we delete all messages
        member = await message.chat.get_member(message.from_user.id)
        if not member.can_delete_messages and member.status != "creator":
            me_mode = True  # Not enough rights, so we'll delete our messages only

    message_list: List[int] = []
    try:
        async for msg in client.iter_history(
            message.chat.id, offset_id=message.reply_to_message.message_id, reverse=True
        ):
            if me_mode and msg.from_user.id != message.from_user.id:
                continue  # Skip messages sent by others if me_mode is True

            if len(message_list) < 100:
                message_list.append(msg.message_id)
            else:
                await client.delete_messages(message.chat.id, message_ids=message_list)
                message_list = []

        if message_list:
            await client.delete_messages(message.chat.id, message_ids=message_list)
    except RPCError as ex:
        logger.error(f"Could not .purge messages due to {ex}")
