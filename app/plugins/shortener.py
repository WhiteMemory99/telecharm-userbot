import httpx
from pyrogram import Client, filters
from pyrogram.types import Message

from app.utils import clean_up, extract_entity_text


@Client.on_message(filters.me & filters.command(['short', 'shorten', 'clck'], prefixes='.'))
async def shorten_url(client: Client, message: Message):
    urls = []
    entities = message.entities or message.caption_entities
    if entities:
        for entity in entities:
            if entity.type == 'url':
                urls.append(extract_entity_text(message.text or message.caption, entity.offset, entity.length))
            elif entity.type == 'text_link':
                urls.append(entity.url)

    if urls:
        short_urls = []
        async with httpx.AsyncClient() as http_client:
            for url in urls[:100]:
                response = await http_client.post('https://clck.ru/--', params={'url': url})
                short_urls.append(response.text)

        await message.edit_text('\n'.join(short_urls), disable_web_page_preview=True)
    else:
        await message.edit_text('Provide a **link** or **text link**, supports several links at once.')
        await clean_up(client, message.chat.id, message.message_id)
