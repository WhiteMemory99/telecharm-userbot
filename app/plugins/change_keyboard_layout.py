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
async def layout_command(client: Client, msg: Message):
    if not msg.reply_to_message:
        await msg.edit_text("You must reply to a message")
        return await clean_up(client, msg.chat.id, msg.message_id)

    text = msg.reply_to_message.text
    current_layout = LAYOUTS[await get_current_layout(text)]
    if get_args(msg.text, 1):
        to_layout = LAYOUTS.get(get_args(msg.text, 1), None)
    else:
        to_layout = [layout for layout in LAYOUTS.values() if layout != current_layout][0]

    changed_text = await change_keyboard_layout(text, current_layout, to_layout)
    if msg.reply_to_message.from_user == msg.from_user:
        await asyncio.gather(
            client.edit_message_text(msg.reply_to_message.chat.id, msg.reply_to_message.message_id, changed_text),
            msg.delete()
        )
    else:
        await msg.edit_text(changed_text)
