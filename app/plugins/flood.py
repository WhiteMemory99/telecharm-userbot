from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message


@Client.on_message(filters.me & filters.command('flood', prefixes='.'))
async def flood_handler(_, message: Message):
    """
    Classic flooder. It's quite dangerous so use it carefully. I'm not responsible for any harm or account losses.
    """
    args = message.text.split(maxsplit=2)
    if len(args) != 3 or not args[1].isdigit():  # Not enough arguments
        await message.edit_text(
            'Pass the number of messages and the text that will be repeated.\n\n`.flood 3 we are victors!`'
        )
    else:
        await message.delete()  # Delete the message with .flood command.
        for _ in range(int(args[1])):
            try:
                await message.reply_text(args[2], quote=False, disable_web_page_preview=True)
            except RPCError as ex:
                logger.error(f'{ex} in .flood, stopping command!')
                break
