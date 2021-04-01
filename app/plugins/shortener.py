import asyncio
from typing import List

import httpx
from pyrogram import Client, filters
from pyrogram.types import Message, MessageEntity

from app.utils import clean_up, extract_entity_text


@Client.on_message(filters.me & filters.command(["short", "clck"], prefixes="."))
async def shorten_url(client: Client, message: Message):
    """
    Shorten URLs contained in the outgoing and/or reply message text.
    """
    urls = []
    entities = message.entities or message.caption_entities
    if entities:  # There are outgoing entities
        urls += get_text_urls(message.text or message.caption, entities)
    if message.reply_to_message:
        entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
        if entities:
            urls += get_text_urls(message.reply_to_message.text or message.reply_to_message.caption, entities)

    if urls:
        async with httpx.AsyncClient() as http_client:
            responses = await asyncio.gather(
                *[http_client.post("https://clck.ru/--", params={"url": url}) for url in urls[:100]]
            )

        await message.edit_text(
            "\n".join(f"<b>-</b> {response.text}" for response in responses if response.status_code == 200),
            disable_web_page_preview=True,
        )
    else:
        await message.edit_text("<b>Reply to message</b> or provide a <b>link</b>, supports up to 100 links.")
        await clean_up(client, message.chat.id, message.message_id)


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
