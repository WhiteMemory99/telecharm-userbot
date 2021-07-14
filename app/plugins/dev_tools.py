from pyrogram import filters

from app.utils import quote_html, Client, Message


@Client.on_message(filters.me & filters.command("bdata", prefixes="."))
async def get_buttons_data(_, message: Message):
    """Get callback_data and urls of all the inline buttons of the message you replied to."""
    reply_message = message.reply_to_message
    if reply_message and reply_message.reply_markup:
        if reply_message.reply_markup.inline_keyboard:
            row_lines = []
            for i, row in enumerate(reply_message.reply_markup.inline_keyboard):
                row_buttons = []
                for button in row:
                    if button.callback_data:
                        data = button.callback_data
                    elif button.url:
                        data = button.url
                    else:
                        continue

                    row_buttons.append(f"<i>{quote_html(button.text)}:</i> <code>{quote_html(data)}</code>")

                buttons = "\n".join(row_buttons)
                row_lines.append(f"<b>Row {i + 1}:</b>\n{buttons}")

            if row_lines:
                await message.edit_text("\n\n".join(row_lines), message_ttl=25)
            else:
                await message.edit_text(
                    "There is no any callback_data or url button inside this keyboard.", message_ttl=5
                )
    else:
        await message.edit_text(
            "Reply to a message containing inline keyboard to extract callback_data and urls.",
            message_ttl=5
        )
