from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message


@Client.on_message(filters.me & filters.reply & filters.command('purge', prefixes='.'))
async def purge(client: Client, message: Message):
    """
    Purge messages in any chat, supports 2 working modes: my messages and all messages.
    """
    args = message.text.split(maxsplit=2)
    me_mode = True if 'me' in args else False

    if message.chat.type in ['group', 'supergroup'] and not me_mode:  # Check admin rights if we delete all messages
        member = await message.chat.get_member(message.from_user.id)
        if not member.can_delete_messages and member.status != 'creator':
            me_mode = True  # Not enough rights, so we'll delete our messages only
    elif message.chat.type == 'channel':
        return  # TODO: Think about channels

    msgs = []
    try:
        async for msg in client.iter_history(  # noqa
                message.chat.id,
                offset_id=message.reply_to_message.message_id,
                reverse=True):
            if me_mode and msg.from_user.id != message.from_user.id:
                continue  # Skip messages sent by other users if the me_mode is True
            else:
                if len(msgs) < 100:
                    msgs.append(msg.message_id)
                else:
                    await client.delete_messages(message.chat.id, message_ids=msgs)
                    msgs = []

        if msgs:
            await client.delete_messages(message.chat.id, message_ids=msgs)
    except RPCError as ex:
        logger.error(f'Could not .purge messages due to {ex}')
