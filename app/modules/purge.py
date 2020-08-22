from loguru import logger
from pyrogram import Client, Filters, Message
from pyrogram.errors import RPCError


@Client.on_message(Filters.me & Filters.reply & Filters.command('purge', prefixes='.'))
async def purge_handler(client: Client, message: Message):
    args = message.text.split(maxsplit=2)
    me_mode = True if 'me' in args else False

    if message.chat.type in ['group', 'supergroup'] and not me_mode:
        member = await message.chat.get_member(message.from_user.id)
        if not member.can_delete_messages and member.status != 'creator':
            me_mode = True
    elif message.chat.type == 'channel':
        return  # TODO: Think about channels

    msgs = []
    async for msg in client.iter_history(  # noqa
            message.chat.id,
            offset=1,
            offset_id=message.reply_to_message.message_id,
            reverse=True):
        if me_mode and msg.from_user.id != message.from_user.id:
            continue
        else:
            msgs.append(msg.message_id)

    try:
        await client.delete_messages(message.chat.id, message_ids=msgs[::-1])
    except RPCError as ex:
        logger.error(f'Could not .purge messages due to {ex}')
