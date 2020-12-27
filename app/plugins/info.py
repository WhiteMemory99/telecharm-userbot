from pyrogram import Client, filters
from pyrogram.types import Message

from app import __version__, config, SysInfo
from app.utils import clean_up, get_args


@Client.on_message(filters.me & filters.command(['start', 'help', 'share'], prefixes='.'))
async def help_command(client: Client, message: Message):
    """
    Builtin help command to access command list and GitHub repo or share this userbot.
    """
    args = get_args(message.text or message.caption)
    if 'ru' in args:  # Russian version requested
        text = f'**Telecharm v{__version__}**:\n\n`.help` - Английская версия.\n\n' \
               f'__[Список команд]({config.GUIDE_LINK_RU})\n[Telecharm на GitHub]({config.GITHUB_LINK})__'
    else:  # English version requested
        text = f'**Telecharm v{__version__}**:\n\n`.help ru` for Russian\n\n' \
               f'__[List of commands]({config.GUIDE_LINK_EN})\n[Telecharm on GitHub]({config.GITHUB_LINK})__'

    await message.edit_text(text, disable_web_page_preview=True)
    await clean_up(client, message.chat.id, message.message_id, clear_after=15)


@Client.on_message(filters.me & filters.command('sys', prefixes='.'))
async def system_information(client: Client, message: Message):
    """
    Show some info about the current system and Telecharm components.
    """
    await message.edit_text(f'**My system info:**\n\n{str(SysInfo())}')

