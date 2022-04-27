from typing import List

from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message

from app.utils.decorators import doc_args


@Client.on_message(filters.me & filters.reply & filters.command("purge", prefixes="."))
@doc_args("me")
async def purge_command(client: Client, message: Message) -> None:
    """
    Bulk delete of messages. Just reply to the oldest message you want to clear to.
    By default, deletes all the messages, unless used in a group without admin privileges.
    You can also force this command to delete only your messages
    by providing `<code>me</code>` argument.
    """
    me_mode = "me" in message.command

    # Check admin rights if we want to delete all messages
    if message.chat.type in {"group", "supergroup"} and not me_mode:
        member = await message.chat.get_member(message.from_user.id)
        if member.status != "creator" and not getattr(member, "can_delete_messages", False):
            me_mode = True  # Not enough rights, so we'll delete our messages only

    message_list: List[int] = []
    try:
        async for history_message in client.get_chat_history(
            message.chat.id, offset_id=message.reply_to_message.id
        ):
            if me_mode and history_message.from_user.id != message.from_user.id:
                continue  # Skip messages sent by others if me_mode is True

            if len(message_list) < 99:
                message_list.append(history_message.id)
            else:
                await client.delete_messages(message.chat.id, message_ids=message_list)
                message_list.clear()

        if message_list:
            await client.delete_messages(message.chat.id, message_ids=message_list)
    except RPCError as ex:
        logger.error(f"Could not .purge messages due to {ex}")
