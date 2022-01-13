import os
import tempfile

from pyrogram import filters
from pyrogram.types import Document
from saucenaopie.exceptions import ImageInvalid, LongLimitReached, SauceNaoError, ShortLimitReached

from app.utils import Client, Message


@Client.on_message(filters.me & filters.command(["sauce", "saucenao"], prefixes="."))
async def find_sauce(client: Client, message: Message):
    """
    Find an art or picture source by replying to a photo or <b>image</b> document.
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
        await message.edit_text("A photo or <b>image</b> document is required.")
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            await message.edit_text("<i>Processing...</i>", message_ttl=0)
            file_path = await client.download_media(
                target_msg, file_name=os.path.join(tempdir, media.file_id)
            )

            try:
                sauce = await client.saucenao.search(file_path)
            except LongLimitReached:
                return await message.edit_text(
                    "Your SauceNao profile reached its daily limit of <b>200 searches</b>."
                )
            except ShortLimitReached:
                return await message.edit_text(
                    "Your SauceNao profile reached its short limit, try again in a few seconds."
                )
            except ImageInvalid:
                return await message.edit_text("The image is bad, couldn't get its sources.")
            except SauceNaoError:
                return await message.edit_text(
                    "Some unexpected error has occurred while processing this picture."
                )

        results = sauce.get_likely_results()
        if results:
            formatted_links = [
                f'{i + 1}. <a href="{r.data.first_url}">{r.index}</a> - {r.similarity:.1f}%'
                for i, r in enumerate(results)
                if r.data.first_url
            ]
            await message.edit_text(
                "Here's this picture <b>sauces</b>:\n\n" + "\n".join(formatted_links),
                message_ttl=35,
            )
        else:
            await message.edit_text("Couldn't find any valid sources of this picture.")
