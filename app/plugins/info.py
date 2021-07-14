from pyrogram import filters

from app import SysInfo, __version__, config
from app.utils import Client, Message


@Client.on_message(filters.me & filters.command(["help", "share"], prefixes="."))
async def help_command(_, message: Message):
    """Built-in help command to access command list and GitHub repo or share this userbot."""
    await message.edit_text(
        f"<b>Telecharm v{__version__}</b>:\n\nFast and simple Telegram userbot based on pyrogram."
        f'\n\n<i><a href="{config.GUIDE_LINK}">List of commands</a>'
        f'\n<a href="{config.GITHUB_LINK}">Telecharm on GitHub</a></i>',
        disable_web_page_preview=True,
        message_ttl=15
    )


@Client.on_message(filters.me & filters.command("sys", prefixes="."))
async def system_information(_, message: Message):
    """Show some info about the current system and Telecharm components."""
    await message.edit_text(str(SysInfo()), message_ttl=10)
