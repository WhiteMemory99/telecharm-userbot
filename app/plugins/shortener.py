import asyncio
from typing import List

from pyrogram import filters
from pyrogram.types import MessageEntity

from app.config import conf
from app.utils import extract_entity_text, Client, Message
from app.utils.decorators import doc_args


@Client.on_message(filters.me & filters.command(["short", "clck"], prefixes="."))
@doc_args("links")
async def shorten_url(client: Client, message: Message):  # TODO: Remove the limit and wrap the message
    """
    Shorten URLs contained in outgoing <b>and/or</b> replied message.
    This command takes up to a hundred links at once, and uses <b>clck.ru</b> developed by Yandex
    because of its simplicity.
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
        responses = await asyncio.gather(
            *[client.http_client.post("https://clck.ru/--", params={"url": url}) for url in urls[:100]]
        )

        await message.edit_text(
            "\n".join(f"<b>-</b> {response.text}" for response in responses if response.status_code == 200),
            disable_web_page_preview=True,
        )
    else:
        await message.edit_text(
            "<b>Reply to message</b> or provide a <b>link</b>, supports up to 100 links at once.",
            message_ttl=conf.default_ttl
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
