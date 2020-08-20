from loguru import logger
from pyrogram import Client, Filters, Message
from pyrogram.errors import RPCError


@Client.on_message(Filters.me & Filters.command('flood', prefixes='.'))
async def flood_handler(_, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) != 3 or not args[1].isdigit():
        await message.edit_text(
            'Передайте число сообщений и текст, который будет повторяться.\n'
            'Pass the number of messages and the text that will be repeated.\n\n`.flood 3 we are victors!`'
        )
    else:
        await message.delete()
        for _ in range(int(args[1])):
            try:
                await message.reply_text(args[2], quote=False, disable_web_page_preview=True)
            except RPCError as ex:
                logger.error(f'{ex} in .flood, stopping command!')
                break


@Client.on_message(Filters.me & Filters.reply & Filters.command('purge', prefixes='.'))
async def purge_handler(client: Client, message: Message):
    args = message.text.split(maxsplit=2)
    me_mode = True if len(args) > 1 and 'me' in args else False

    if message.chat.type in ['group', 'supergroup'] and len(args) > 1:
        member = await message.chat.get_member(message.from_user.id)
        if not member.can_delete_messages and member.status != 'creator' and not me_mode:
            me_mode = True
    elif message.chat.type == 'channel':
        return  # TODO: Think about channels

    msgs = []
    async for msg in client.iter_history(message.chat.id, offset_id=message.reply_to_message.message_id, reverse=True):
        if me_mode and msg.from_user.id != message.from_user.id:
            continue
        else:
            msgs.append(msg.message_id)

    try:
        await client.delete_messages(message.chat.id, message_ids=msgs)
    except RPCError as ex:
        logger.error(f'Could not .purge messages due to {ex}')
