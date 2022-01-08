"""This module commands are meant for advanced users and developers only."""

import asyncio

from loguru import logger
from pyrogram import filters
from pyrogram.errors import FloodWait, RPCError

from app.utils import Client, Message, quote_html
from app.utils.decorators import doc_args


@Client.on_message(filters.me & filters.command("flood", prefixes="."))
@doc_args("times", "text")
async def flood_command(_, message: Message):
    """
    Send a specified number of messages consecutively. Only for development and testing purposes.
    Using this command in malicious ways may lead to your profile loss,
    I'm not responsible for any damage caused.
    """
    args = message.get_args()
    if len(args) != 2 or not args[0].isdigit():  # Not enough arguments
        await message.edit_text(
            "Pass the number of messages and the text that will be repeated."
            "\n\n<code>.flood 3 we are victors!</code>",
        )
    else:
        await message.delete()
        for _ in range(int(args[0])):
            try:
                await message.reply_text(
                    quote_html(args[1]), quote=False, disable_web_page_preview=True
                )
            except FloodWait as ex:
                logger.error(f"Sleeping for {ex.x} seconds in .flood")
                await asyncio.sleep(ex.x)
            except RPCError as ex:
                logger.error(f"{ex} in .flood, stopping command!")
                break


@Client.on_message(filters.me & filters.command("bdata", prefixes="."))
async def get_buttons_data(_, message: Message):
    """
    Get callback_data and urls of all the inline buttons from the message you replied to.
    This command is especially useful for developers, and lets you quickly unpack any keyboard.
    """
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

                    row_buttons.append(
                        f"<i>{quote_html(button.text)}:</i> <code>{quote_html(data)}</code>"
                    )

                buttons = "\n".join(row_buttons)
                row_lines.append(f"<b>Row {i + 1}:</b>\n{buttons}")

            if row_lines:
                await message.edit_text("\n\n".join(row_lines), message_ttl=25)
            else:
                await message.edit_text(
                    "There is no any callback_data or url button inside this keyboard.",
                    message_ttl=5,
                )
    else:
        await message.edit_text(
            "Reply to a message containing inline keyboard to extract callback_data and urls.",
            message_ttl=5,
        )
