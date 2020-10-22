from pyrogram import Client, filters
from pyrogram.errors import FirstnameInvalid, FloodWait, UsernameInvalid, UsernameNotModified, UsernameOccupied
from pyrogram.types import Message

from utils import clean_up


@Client.on_message(filters.me & filters.command(['stat', 'stats'], prefixes='.'))
async def stats_handler(client: Client, message: Message):
    """
    Gather profile stats containing chats info to share it to anyone.
    """
    args = message.text.split(maxsplit=2)
    await message.edit_text(f'{message.text}\n__Gathering info...__')

    user_list = []
    peak_unread_chat = None
    total_chats = channels = privates = groups = pinned = unread = peak_unread_count = bots = 0
    async for dialog in client.iter_dialogs():  # noqa
        total_chats += 1
        if dialog.is_pinned:
            pinned += 1
        if dialog.unread_messages_count > 0:
            unread += 1
            if dialog.unread_messages_count > peak_unread_count:
                peak_unread_count = dialog.unread_messages_count
                peak_unread_chat = dialog.chat.title

        if dialog.chat.type == 'channel':
            channels += 1
        elif dialog.chat.type in ['group', 'supergroup']:
            groups += 1
        else:
            privates += 1
            user_list.append(dialog.chat.id)

    full_users = await client.get_users(user_list)
    for user in full_users:
        if user.is_bot:
            bots += 1

    contacts = await client.get_contacts_count()
    if 'ru' in args:  # Russian version requested
        if peak_unread_chat:
            unread_data = f'**{peak_unread_count}** в `{peak_unread_chat}`'
        else:
            unread_data = f'**{peak_unread_count}**'

        text = f'Всего чатов: **{total_chats}**\nЗакреплённых: **{pinned}**\nНепрочитанных: **{unread}**\n' \
               f'Каналов: **{channels}**\nПриватных: **{privates}**\nБотов: **{bots}**\nГрупп: **{groups}**\n\n' \
               f'Контактов в Telegram: **{contacts}**\nМаксимум непрочитанных за чат: {unread_data}'
    else:  # English version requested
        if peak_unread_chat:
            unread_data = f'**{peak_unread_count}** in `{peak_unread_chat}`'
        else:
            unread_data = f'**{peak_unread_count}**'

        text = f'Total chats: **{total_chats}**\nPinned: **{pinned}**\nUnread: **{unread}**\n' \
               f'Channels: **{channels}**\nPrivates: **{privates}**\nBots: **{bots}**\nGroups: **{groups}**\n\n' \
               f'Telegram contacts: **{contacts}**\nPeak value of unread per chat: {unread_data}'

    await message.edit_text(text)
    await clean_up(client, message.chat.id, message.message_id, clear_after=20)


@Client.on_message(filters.me & filters.command('name', prefixes='.'))
async def name_handler(client: Client, message: Message):
    """
    Change my profile name, this command is flexible and has an auto-balancer for long names.
    """
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
        else:  # A quite complex name specified, so we have to balance it a little
            divider = len(args) // 2
            first_name = ' '.join(args[:divider])[:64]
            last_name = ' '.join(args[divider:])[:64]

        try:
            await client.update_profile(first_name=first_name, last_name=last_name)
            result = f'{first_name} {last_name}' if last_name else first_name
            await message.edit_text(f'Your name\'s been changed to:\n`{result}`')
        except FirstnameInvalid:
            await message.edit_text('Your new first name is invalid.')
        except FloodWait as ex:
            await message.edit_text(f'**FloodWait**, retry in `{ex.x}` seconds.')

    await clean_up(client, message.chat.id, message.message_id)


@Client.on_message(filters.me & filters.command('username', prefixes='.'))
async def username_handler(client: Client, message: Message):
    """
    Change my profile username. Supports "del" argument to delete the current username if there is one.
    """
    username = message.text.partition(' ')[2].lstrip('@')
    if not username:
        await message.edit_text('Pass your new username.\n`.username del` to delete it.')
    else:
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
                await message.edit_text('This username is invalid.')
        except FloodWait as ex:
            await message.edit_text(f'**FloodWait**, retry in `{ex.x}` seconds.')

    await clean_up(client, message.chat.id, message.message_id)


@Client.on_message(filters.me & filters.command(['bio', 'about'], prefixes='.'))
async def bio_handler(client: Client, message: Message):
    """
    Change my about info block. Supports "del" argument to clear the current bio.
    """
    args = message.text.partition(' ')[2]
    if not args:
        await message.edit_text('Pass your new about info.\n`.bio del` to delete it.')
    else:
        if args == 'del':
            args = ''
            text = 'Your bio\'s been deleted.'
        else:
            text = f'Your bio\'s been updated to:\n`{args[:70]}`'

        try:
            await client.update_profile(bio=args[:70])  # Max bio length is 70 chars
            await message.edit_text(text)
        except FloodWait as ex:
            await message.edit_text(f'**FloodWait**, retry in `{ex.x}` seconds.')

    await clean_up(client, message.chat.id, message.message_id)
