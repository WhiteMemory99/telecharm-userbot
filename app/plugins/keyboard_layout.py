import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from app.utils import get_args, clean_up

LAYOUTS = {
    'ru': "ё1234567890-=Ё!\"№;%:?*()_+йцукенгшщзхъ\\ЙЦУКЕНГШЩЗХЪ/фывапролджэФЫВАПРОЛДЖЭячсмитьбю.ЯЧСМИТЬБЮ,",
    'en': '`1234567890-=~!@#$%^&*()_+qwertyuiop[]\\QWERTYUIOP{}|asdfghjkl;\'ASDFGHJKL:"zxcvbnm,./ZXCVBNM<>?',
}


async def get_current_layout(text: str) -> str:
    layouts = {}
    for key, value in LAYOUTS.items():
        layouts[len([v for v in text if v in value])] = key
    return layouts[max(layouts.keys())]


async def change_keyboard_layout(text: str, from_layout: str, to_layout: str) -> str:
    table = str.maketrans(from_layout, to_layout)
    return text.translate(table)


@Client.on_message(filters.me & filters.command("layout", prefixes="."))
async def layout_command(client: Client, message: Message):
    """
    Change the keyboard layout of a message.

    Example:
        from: руддщ!
        to: hello!
    """
    if not message.reply_to_message:
        await message.edit_text("You must reply to a message.")
        return await clean_up(client, message.chat.id, message.message_id)

    text = message.reply_to_message.text or message.reply_to_message.caption
    entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
    current_layout = LAYOUTS[await get_current_layout(text)]

    args = get_args(message.text, 1)
    if args:
        to_layout = LAYOUTS.get(args, None)
    else:
        to_layout = [layout for layout in LAYOUTS.values() if layout != current_layout][0]

    changed_text = await change_keyboard_layout(text, current_layout, to_layout)
    if message.reply_to_message.from_user.id == message.from_user.id:
        await asyncio.gather(
            client.edit_message_text(
                message.reply_to_message.chat.id,
                message.reply_to_message.message_id,
                changed_text,
                entities=entities,
            ),
            message.delete(),
        )
    else:
        await message.edit_text(changed_text, entities=entities)
        await clean_up(client, message.chat.id, message.message_id, 60)
