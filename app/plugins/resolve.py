from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.me & filters.command('resolve', prefixes='.'))  # WIP
async def resolve_handler(_, message: Message):
    if message.reply_to_message:
        await message.edit_text(
            f'{message.reply_to_message.from_user.first_name} **ID** is `{message.reply_to_message.from_user.id}`')
