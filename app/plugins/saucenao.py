import os
import tempfile
from typing import List, Optional

from pyrogram import filters
from pyrogram.types import Document, MessageEntity
from saucenaopie import AsyncSauceNao
from saucenaopie.exceptions import ImageInvalid, LongLimitReached, SauceNaoError, ShortLimitReached
from saucenaopie.types.response import SauceResponse

from app.utils import Client, Message, extract_entity_text


def get_first_url(entities: List[MessageEntity], text: str) -> Optional[str]:
    """Iterate the message entities and get the first URL if there is any."""
    for entity in entities:
        if entity.type == "url":
            return extract_entity_text(text, entity.offset, entity.length)
        elif entity.type == "text_link":
            return entity.url


async def search_saucenao(
    saucenao: AsyncSauceNao, message: Message, source: str, from_url: bool = False
) -> Optional[SauceResponse]:
    """Send a search request to the SauceNao API and handle possible errors."""
    try:
        return await saucenao.search(source, from_url=from_url)
    except LongLimitReached:
        await message.edit_text(
            "Your SauceNao profile reached its daily limit of <b>200 searches</b>."
        )
    except ShortLimitReached:
        await message.edit_text(
            "Your SauceNao profile reached its short limit, try again in a few seconds."
        )
    except ImageInvalid:
        await message.edit_text("The image is bad, couldn't get its sources.")
    except SauceNaoError:
        await message.edit_text(
            "Some unexpected error has occurred while processing this picture."
        )


@Client.on_message(filters.me & filters.command(["sauce", "saucenao"], prefixes="."))
async def find_sauce(client: Client, message: Message):
    """
    Find an art or picture source by replying to a photo, <b>image</b> document, or message with a
    direct URL to the picture. Note, that only the first URL in the message is being checked.

    If successful, you will receive a list of potential sources for the image.
    """
    if client.saucenao is None:
        return await message.edit_text(
            "You must add your <b>SauceNao API</b> key to the <code>.env</code> "
            "file and restart Telecharm in order to use this command."
        )

    target_msg = message.reply_to_message if message.reply_to_message else message
    media = target_msg.photo or target_msg.document

    if media is None or (isinstance(media, Document) and "image" not in media.mime_type):
        entities = target_msg.entities or target_msg.caption_entities
        url = get_first_url(entities, target_msg.text or target_msg.caption)
        if url:
            sauce = await search_saucenao(client.saucenao, message, url, from_url=True)
        else:
            return await message.edit_text(
                "A photo, <b>image</b> document, or message with a valid direct URL is required.",
                message_ttl=5,
            )
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            await message.edit_text("<i>Processing...</i>", message_ttl=0)
            file_path = await client.download_media(
                target_msg, file_name=os.path.join(tempdir, media.file_id)
            )
            sauce = await search_saucenao(client.saucenao, message, file_path)

    if not sauce:
        return

    results = sauce.get_likely_results()
    formatted_links = [
        f'{i + 1}. <a href="{r.data.first_url}">{r.index}</a> - {r.similarity:.1f}%'
        for i, r in enumerate(results)
        if r.data.first_url
    ]
    if formatted_links:
        await message.edit_text(
            "Here are this picture's <b>sauces</b>:\n\n" + "\n".join(formatted_links),
            message_ttl=35,
        )
    else:
        await message.edit_text("Couldn't find any valid sources of this picture.")
