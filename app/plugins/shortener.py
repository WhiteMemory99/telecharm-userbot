import asyncio
from typing import List

from pyrogram import filters
from pyrogram.types import MessageEntity

from app import config
from app.utils import extract_entity_text, Client, Message


@Client.on_message(filters.me & filters.command(["short", "clck"], prefixes="."))
async def shorten_url(client: Client, message: Message):
    """Shorten URLs contained in outgoing and/or reply messages."""
    urls = []
    entities = message.entities or message.caption_entities
    if entities:  # There are outgoing entities
        urls += get_text_urls(message.text or message.caption, entities)
    if message.reply_to_message:
        entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
        if entities:
            urls += get_text_urls(message.reply_to_message.text or message.reply_to_message.caption, entities)

    if urls:
        responses = await asyncio.gather(
            *[client.http_client.post("https://clck.ru/--", params={"url": url}) for url in urls[:100]]
        )

        await message.edit_text(
            "\n".join(f"<b>-</b> {response.text}" for response in responses if response.status_code == 200),
            disable_web_page_preview=True,
        )
    else:  # TODO: Remove the limit and wrap the message
        await message.edit_text(
            "<b>Reply to message</b> or provide a <b>link</b>, supports up to 100 links at once.",
            message_ttl=config.DEFAULT_TTL
        )


def get_text_urls(text: str, entities: List[MessageEntity]) -> list:
    """
    Get all the links or text links from the given text.

    :param text: Original message text.
    :param entities: Message entities
    :return:
    """
    urls = []
    for entity in entities:
        if entity.type == "url":
            urls.append(extract_entity_text(text, entity.offset, entity.length))
        elif entity.type == "text_link":
            urls.append(entity.url)

    return urls
