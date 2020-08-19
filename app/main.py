from loguru import logger
from pyrogram import Client, Filters, Message

import config


app = Client(
    session_name=config.USER_PHONE[1:],
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    phone_number=config.USER_PHONE
)


@app.on_message(Filters.me & Filters.command(['start', 'help'], prefixes='.'))
async def help_handler(_, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) > 1 and args[1] == 'en':
        text = '**Telecharm v0.1.0**:\n\n`.help` - Show this message.\n`.stats` - My profile stats.\n' \
               '`.flood` - Flood messages.\n`.purge` - Purge messages\n\n' \
               f'__[More on commands]({config.GUIDE_LINK_EN})\n[Telecharm on GitHub]({config.GITHUB_LINK})__'
    else:
        text = '**Telecharm v0.1.0**:\n`.help en` for English\n\n`.help` - Показать это сообщение.\n' \
               '`.stats` - Статистика моего профиля.\n`.flood` - Флуд сообщениями.\n`.purge` - Очистка сообщений \n\n' \
               f'__[Подробнее о командах]({config.GUIDE_LINK_RU})\n[Telecharm на GitHub]({config.GITHUB_LINK})__'

    await message.edit_text(text, disable_web_page_preview=True)


@app.on_message(Filters.me & Filters.command('flood', prefixes='.'))
async def flood_handler(_, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) != 3 or not args[1].isdigit():
        await message.edit_text(
            'Передайте число сообщений и текст, который будет повторяться.\n'
            'Pass the number of messages and the text that will be repeated.\n\n`.flood 3 we are victors!`'
        )
    elif int(args[1]) > 300:
        await message.edit_text(
            'Нельзя вызывать более **300** сообщений за один раз.\nNo more than **300** messages allowed in one run')
    else:
        await message.delete()
        for _ in range(int(args[1])):
            try:
                await message.reply_text(args[2], quote=False, disable_web_page_preview=True)
            except Exception as ex:
                logger.error(f'{ex} in .flood, stopping command!')
                break


@app.on_message(Filters.me & Filters.reply & Filters.command('purge', prefixes='.'))
async def purge_handler(client: Client, message: Message):
    args = message.text.split(maxsplit=2)
    me_mode = True if len(args) > 1 and args[1] == 'me' else False

    if message.chat.type in ['group', 'supergroup'] and len(args) > 1:
        member = await message.chat.get_member(message.from_user.id)
        if not member.can_delete_messages and member.status != 'creator' and not me_mode:
            me_mode = True
    elif message.chat.type == 'channel':
        return  # TODO: Think about channels

    msgs = []
    async for msg in client.iter_history(message.chat.id, offset_id=message.reply_to_message.message_id, reverse=True):
        try:
            if me_mode and msg.from_user.id != message.from_user.id:
                continue
            else:
                msgs.append(msg.message_id)
        except Exception as ex:
            logger.error(f'{ex} in .purge, stopping command!')
            break

    await client.delete_messages(message.chat.id, message_ids=msgs)


@app.on_message(Filters.me & Filters.command(['stat', 'stats'], prefixes='.'))  # TODO: WE NEED MORE STATS!
async def stats_handler(client: Client, message: Message):
    args = message.text.split(maxsplit=2)
    all_chats = channels = privates = groups = pinned = unread = 0
    async for dialog in client.iter_dialogs():  # noqa
        all_chats += 1
        if dialog.is_pinned:
            pinned += 1
        if dialog.unread_messages_count > 0:
            unread += 1

        if dialog.chat.type == 'channel':
            channels += 1
        elif dialog.chat.type in ['group', 'supergroup']:
            groups += 1
        else:
            privates += 1

    contacts = await client.get_contacts_count()
    if len(args) > 1 and args[1] == 'en':
        text = f'My ID: `{message.from_user.id}`\n\nTotal chats: **{all_chats}**\n' \
               f'Pinned: **{pinned}**\nUnread: **{unread}**\nChannels: **{channels}**\n' \
               f'Private: **{privates}**\nGroups: **{groups}**\n\nTelegram contacts: **{contacts}**'
    else:
        text = f'Мой ID: `{message.from_user.id}`\n\nВсего чатов: **{all_chats}**\n' \
               f'Закреплённых: **{pinned}**\nНепрочитанных: **{unread}**\nКаналов: **{channels}**\n' \
               f'Приватных: **{privates}**\nГрупп: **{groups}**\n\nКонтактов в Telegram: **{contacts}**'

    await message.edit_text(text)


if __name__ == '__main__':
    app.run()
