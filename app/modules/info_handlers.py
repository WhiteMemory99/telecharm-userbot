from pyrogram import Client, Filters, Message

import config


@Client.on_message(Filters.me & Filters.command(['start', 'help'], prefixes='.'))
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


@Client.on_message(Filters.me & Filters.command(['stat', 'stats'], prefixes='.'))  # TODO: WE NEED MORE STATS!
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
