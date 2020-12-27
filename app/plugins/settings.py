from pyrogram import Client, filters
from pyrogram.types import Message

from app.storage import json_settings
from app.utils import clean_up


@Client.on_message(filters.me & filters.command('cleanup', prefixes='.'))
async def clean_up_switcher(client: Client, message: Message):
    """
    Turn on/off cleaning up mode that deletes messages some time after editing them.
    """
    last_value = json_settings.data.get('clean_up', False)
    json_settings.set('clean_up', not last_value)

    status = 'off' if last_value else 'on'
    await message.edit_text(f'Clean up is **{status}**.')
    await clean_up(client, message.chat.id, message.message_id)
