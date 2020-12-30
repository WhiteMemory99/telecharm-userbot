from pyrogram import Client, filters
from pyrogram.types import Message

from app import __version__, config, SysInfo
from app.utils import clean_up, get_args


@Client.on_message(filters.me & filters.command(['help', 'share'], prefixes='.'))
async def help_command(client: Client, message: Message):
    """
    Builtin help command to access command list and GitHub repo or share this userbot.
    """
    await message.edit_text(
        f'<b>Telecharm v{__version__}</b>:\n\nFast and simple Telegram userbot based on pyrogram.'
        f'\n\n<i><a href="{config.GUIDE_LINK_EN}">List of commands</a>'
        f'\n<a href="{config.GITHUB_LINK}">Telecharm on GitHub</a></i>', 
        disable_web_page_preview=True
    )
    await clean_up(client, message.chat.id, message.message_id, clear_after=15)


@Client.on_message(filters.me & filters.command('sys', prefixes='.'))
async def system_information(client: Client, message: Message):
    """
    Show some info about the current system and Telecharm components.
    """
    await message.edit_text(str(SysInfo()))
    await clean_up(client, message.chat.id, message.message_id, clear_after=10)

