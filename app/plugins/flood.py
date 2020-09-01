from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message


@Client.on_message(filters.me & filters.command('flood', prefixes='.'))
async def flood_handler(_, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) != 3 or not args[1].isdigit():
        await message.edit_text(
            'Pass the number of messages and the text that will be repeated.\n\n`.flood 3 we are victors!`'
        )
    else:
        await message.delete()
        for _ in range(int(args[1])):
            try:
                await message.reply_text(args[2], quote=False, disable_web_page_preview=True)
            except RPCError as ex:
                logger.error(f'{ex} in .flood, stopping command!')
                break
