from pyrogram import Client, Filters, Message
from pyrogram.errors import FirstnameInvalid, UsernameInvalid, UsernameNotModified, UsernameOccupied

import config


@Client.on_message(Filters.me & Filters.command(['start', 'help'], prefixes='.'))
async def help_handler(_, message: Message):
    args = message.text.split(maxsplit=2)
    if 'ru' in args:
        text = f'**Telecharm v{config.TELECHARM_VERSION}**:\n\n`.help` - Показать это сообщение.\n' \
               '`.stats` - Статистика моего профиля.\n`.flood` - Флуд сообщениями.\n`.purge` - Очистка сообщений\n' \
               '`.name` - Сменить моё имя\n`.username` - Сменить мой юзернейм\n`.bio` - Отредактировать "О себе"\n\n' \
               f'__[Подробнее о командах]({config.GUIDE_LINK_RU})\n[Telecharm на GitHub]({config.GITHUB_LINK})__'
    else:
        text = f'**Telecharm {config.TELECHARM_VERSION}**:\n`.help ru` for Russian\n\n`.help` - Show this message.\n' \
               '`.stats` - My profile stats.\n`.flood` - Flood messages.\n`.purge` - Purge messages\n' \
               '`.name` - Change my name\n`.username` - Change my username\n`.bio` - Edit my about info\n\n' \
               f'__[More on commands]({config.GUIDE_LINK_EN})\n[Telecharm on GitHub]({config.GITHUB_LINK})__'

    await message.edit_text(text, disable_web_page_preview=True)


@Client.on_message(Filters.me & Filters.command(['stat', 'stats'], prefixes='.'))  # TODO: WE NEED MORE STATS!
async def stats_handler(client: Client, message: Message):
    args = message.text.split(maxsplit=2)
    await message.edit_text(f'{message.text}\nGathering info...')
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
    if 'ru' in args:
        text = f'Мой ID: `{message.from_user.id}`\n\nВсего чатов: **{all_chats}**\n' \
               f'Закреплённых: **{pinned}**\nНепрочитанных: **{unread}**\nКаналов: **{channels}**\n' \
               f'Приватных: **{privates}**\nГрупп: **{groups}**\n\nКонтактов в Telegram: **{contacts}**'
    else:
        text = f'My ID: `{message.from_user.id}`\n\nTotal chats: **{all_chats}**\n' \
               f'Pinned: **{pinned}**\nUnread: **{unread}**\nChannels: **{channels}**\n' \
               f'Private: **{privates}**\nGroups: **{groups}**\n\nTelegram contacts: **{contacts}**'

    await message.edit_text(text)


@Client.on_message(Filters.me & Filters.command('name', prefixes='.'))
async def name_handler(client: Client, message: Message):
    args = message.text.split()[1:]
    if not args:
        await message.edit_text('Pass your new name.\n`.name I\'m a superman!`')
    else:
        if len(args) == 1:
            first_name = args[0][:64]
            last_name = ''
        elif len(args) == 2:
            first_name = args[0][:64]
            last_name = args[1][:64]
        else:
            first_name = ' '.join(args[:len(args) // 2])[:64]
            last_name = ' '.join(args[len(args) // 2:])[:64]

        try:
            await client.update_profile(first_name=first_name, last_name=last_name)
            result = f'{first_name} {last_name}' if last_name else first_name
            await message.edit_text(f'Your name\'s been changed to:\n`{result}`')
        except FirstnameInvalid:
            await message.edit_text('Your new first name is unacceptable.')


@Client.on_message(Filters.me & Filters.command('username', prefixes='.'))
async def username_handler(client: Client, message: Message):
    args = message.text.split(maxsplit=2)[1:]
    if not args:
        await message.edit_text('Pass your new username.\n`.username del` to remove it.')
    else:
        username = args[0].lstrip('@')
        if username == 'del':
            username = None
            text = 'Your username\'s been deleted.'
        else:
            text = f'Your username\'s been changed to:\n`@{username}`'

        try:
            await client.update_username(username)
            await message.edit_text(text)
        except UsernameNotModified:
            await message.edit_text('This username is not different from the current one.')
        except UsernameOccupied:
            await message.edit_text('This username is already taken.')
        except UsernameInvalid:
            if len(username) > 32:
                await message.edit_text('This username is too long.')
            else:
                await message.edit_text('This username is unacceptable.')


@Client.on_message(Filters.me & Filters.command(['bio', 'about'], prefixes='.'))
async def bio_handler(client: Client, message: Message):
    args = message.text.partition(' ')[2]
    if not args:
        await message.edit_text('Pass your new about info.\n`.bio del` to remove it.')
    else:
        if args == 'del':
            args = ''
            text = 'Your bio\'s been deleted.'
        else:
            text = f'Your bio\'s been updated to:\n`{args[:70]}`'

        await message.edit_text(text)
        await client.update_profile(bio=args[:70])
