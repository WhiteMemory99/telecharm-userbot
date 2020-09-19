from pyrogram import Client, filters
from pyrogram.types import Message

import config
from modules import clean_up
from storage import jstorage


@Client.on_message(filters.me & filters.command(['start', 'help'], prefixes='.'))
async def help_handler(client: Client, message: Message):
    """
    Builtin help command to access command list and GitHub repo.
    """
    args = message.text.split(maxsplit=2)
    if 'ru' in args:  # Russian version requested
        text = f'**Telecharm v{config.TELECHARM_VERSION}**:\n\n`.help` - Английская версия.\n\n' \
               f'__[Список команд]({config.GUIDE_LINK_RU})\n[Telecharm на GitHub]({config.GITHUB_LINK})__'
    else:  # English version requested
        text = f'**Telecharm v{config.TELECHARM_VERSION}**:\n\n`.help ru` for Russian\n\n' \
               f'__[List of commands]({config.GUIDE_LINK_EN})\n[Telecharm on GitHub]({config.GITHUB_LINK})__'

    await message.edit_text(text, disable_web_page_preview=True)
    await clean_up(client, message.chat.id, message.message_id, clear_after=15)


@Client.on_message(filters.me & filters.command('cleanup', prefixes='.'))
async def clean_up_switcher(client: Client, message: Message):
    """
    Turn on/off cleaning up mode that deletes messages some time after editing them.
    """
    last_value = jstorage.data.get('clean_up', False)
    jstorage.write('clean_up', not last_value)

    status = 'off' if last_value else 'on'
    await message.edit_text(f'Clean up is **{status}**.')
    await clean_up(client, message.chat.id, message.message_id)
