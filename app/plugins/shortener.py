from typing import List

import httpx
from pyrogram import Client, filters
from pyrogram.types import Message, MessageEntity

from app.utils import clean_up, extract_entity_text


@Client.on_message(filters.me & filters.command(['short', 'shorten', 'clck'], prefixes='.'))
async def shorten_url(client: Client, message: Message):
    """
    Shorten URLs contained in the outgoing or reply message text.
    """
    urls = None
    entities = message.entities or message.caption_entities
    if entities:
        urls = get_text_urls(message.text or message.caption, entities)
    elif message.reply_to_message:  # Outgoing entities are empty, but there is a reply
        entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
        if entities:
            urls = get_text_urls(message.reply_to_message.text or message.reply_to_message.caption, entities)

    if urls:
        short_urls = []
        await message.edit_text('__Generating...__')
        async with httpx.AsyncClient() as http_client:
            for url in urls[:100]:
                response = await http_client.post('https://clck.ru/--', params={'url': url})
                short_urls.append(response.text)

        await message.edit_text('\n'.join(short_urls), disable_web_page_preview=True)
    else:
        await message.edit_text('**Reply to message** or provide a **link**, supports up to 100 links.')
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
        if entity.type == 'url':
            urls.append(extract_entity_text(text, entity.offset, entity.length))
        elif entity.type == 'text_link':
            urls.append(entity.url)

    return urls
