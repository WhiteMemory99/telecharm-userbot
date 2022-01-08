import asyncio

from pyrogram import filters

from app.utils import Client, Message
from app.utils.decorators import doc_args

LAYOUTS = {
    "ru": (
        'ё1234567890-=Ё!"№;%:?*()_+йцукенгшщзхъ\\'
        "ЙЦУКЕНГШЩЗХЪ/фывапролджэФЫВАПРОЛДЖЭячсмитьбю.ЯЧСМИТЬБЮ,"
    ),
    "en": (
        "`1234567890-=~!@#$%^&*()_+qwertyuiop[]\\"
        "QWERTYUIOP{}|asdfghjkl;'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?"
    ),
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
@doc_args("language code")
async def layout_command(client: Client, message: Message):
    """
    Change the keyboard layout of a message. The language code is <b>optional</b>.
    If the message is yours, it will be edited.
    If the message isn't yours, the new one will be sent.
    <b>Example of the command in action:</b> <code>Ghbdtn</code> >> <code>Привет</code>.
    """
    if not message.reply_to_message:
        await message.edit_text("You must reply to a message to change its layout.")

    text = message.reply_to_message.text or message.reply_to_message.caption
    entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
    current_layout = LAYOUTS[await get_current_layout(text)]

    if args := message.get_args():
        to_layout = LAYOUTS.get(args[0].lower(), None)
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
        await message.edit_text(changed_text, entities=entities, message_ttl=0)
