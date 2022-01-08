from typing import List

from loguru import logger
from pyrogram import filters
from pyrogram.errors import RPCError

from app.utils import Client, Message
from app.utils.decorators import doc_args


@Client.on_message(filters.me & filters.reply & filters.command("purge", prefixes="."))
@doc_args("me")
async def purge_command(client: Client, message: Message):
    """
    Bulk delete of messages. Just reply to the oldest message you want to clear to.
    By default, deletes all the messages, unless used in a group without admin privileges.
    You can also force this command to delete only your messages
    by providing `<code>me</code>` argument.
    """
    me_mode = "me" in message.get_args()

    if (
        message.chat.type in ("group", "supergroup") and not me_mode
    ):  # Check admin rights if we delete all messages
        member = await message.chat.get_member(message.from_user.id)
        if member.status != "creator" and not member.can_delete_messages:
            me_mode = True  # Not enough rights, so we'll delete our messages only

    message_list: List[int] = []
    try:
        async for history_message in client.iter_history(
            message.chat.id, offset_id=message.reply_to_message.message_id, reverse=True
        ):
            if me_mode and history_message.from_user.id != message.from_user.id:
                continue  # Skip messages sent by others if me_mode is True

            if len(message_list) < 99:
                message_list.append(history_message.message_id)
            else:
                await client.delete_messages(message.chat.id, message_ids=message_list)
                message_list.clear()

        if message_list:
            await client.delete_messages(message.chat.id, message_ids=message_list)
    except RPCError as ex:
        logger.error(f"Could not .purge messages due to {ex}")
