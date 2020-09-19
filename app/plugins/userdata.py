from pyrogram import Client, filters
from pyrogram.errors import FirstnameInvalid, UsernameInvalid, UsernameNotModified, UsernameOccupied
from pyrogram.types import Message

from modules import clean_up


@Client.on_message(filters.me & filters.command(['stat', 'stats'], prefixes='.'))  # TODO: WE NEED MORE STATS!
async def stats_handler(client: Client, message: Message):
    """
    Gather profile stats containing chats info to share it to anyone.
    """
    args = message.text.split(maxsplit=2)
    await message.edit_text(f'{message.text}\n__Gathering info...__')

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
    if 'ru' in args:  # Russian version requested
        text = f'Всего чатов: **{all_chats}**\nЗакреплённых: **{pinned}**\nНепрочитанных: **{unread}**\nКаналов: ' \
               f'**{channels}**\nПриватных: **{privates}**\nГрупп: **{groups}**\n\nКонтактов в Telegram: **{contacts}**'
    else:  # English version requested
        text = f'Total chats: **{all_chats}**\nPinned: **{pinned}**\nUnread: **{unread}**\nChannels: **{channels}**\n' \
               f'Private: **{privates}**\nGroups: **{groups}**\n\nTelegram contacts: **{contacts}**'

    await message.edit_text(text)
    await clean_up(client, message.chat.id, message.message_id, clear_after=15)


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
            first_name = ' '.join(args[:len(args) // 2])[:64]
            last_name = ' '.join(args[len(args) // 2:])[:64]

        try:
            await client.update_profile(first_name=first_name, last_name=last_name)
            result = f'{first_name} {last_name}' if last_name else first_name
            await message.edit_text(f'Your name\'s been changed to:\n`{result}`')
        except FirstnameInvalid:
            await message.edit_text('Your new first name is invalid.')

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

        await message.edit_text(text)
        await client.update_profile(bio=args[:70])  # Max bio length is 70 chars

    await clean_up(client, message.chat.id, message.message_id)
