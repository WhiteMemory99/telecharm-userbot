import html
import os
import tempfile
from decimal import Decimal

import httpx
from pyrogram import Client, filters
from pyrogram.types import Animation, Document, Message, Video

from app.utils import clean_up

try:
    import cv2
except ImportError:
    cv2 = None


API_URL = "https://trace.moe/api/search"
MAL_URL = "https://myanimelist.net/anime/{anime_id}"
ANILIST_URL = "https://anilist.co/anime/{anime_id}"


@Client.on_message(filters.me & filters.command(["anime", "whatanime"], prefixes="."))
async def find_anime(client: Client, message: Message):
    """
    Get info about an anime based on a photo/video/GIF/document.
    """
    target_msg = message.reply_to_message if message.reply_to_message else message
    media = target_msg.photo or target_msg.video or target_msg.animation or target_msg.document

    if media is None or (isinstance(media, Document) and "image" not in media.mime_type):
        await message.edit_text("A photo, video, GIF or <b>image</b> document is required.")
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            await message.edit_text("<i>Processing...</i>")
            file_path = await client.download_media(target_msg, file_name=os.path.join(tempdir, media.file_id))
            if isinstance(media, Animation) or isinstance(media, Video):
                if cv2 is not None:
                    file_path = get_video_frame(file_path)
                else:
                    await message.edit_text("This media type requires <code>opencv-python</code>.")
                    return await clean_up(client, message.chat.id, message.message_id)

            async with httpx.AsyncClient(timeout=10) as http_client:
                try:
                    response = await http_client.post(API_URL, files={"image": open(file_path, "rb")})
                    response.raise_for_status()
                    answer = response.json()
                except httpx.ReadTimeout:
                    answer = "Failed to get info about this anime:\n<code>Read Timeout</code>"
                except httpx.HTTPStatusError as ex:
                    description = httpx.codes.get_reason_phrase(ex.response.status_code)
                    answer = f"Failed to get info about this anime:\n<code>{description}</code>"

        if isinstance(answer, str):  # Error
            await message.edit_text(answer)
        else:
            text = get_anime_info(answer["docs"][0])  # noqa
            await message.edit_text(text, disable_web_page_preview=True)
            return await clean_up(client, message.chat.id, message.message_id, clear_after=15)

    await clean_up(client, message.chat.id, message.message_id)


def get_video_frame(file_path: str) -> str:
    """
    Get a frame of any video or GIF with opencv. Requires opencv extras.

    :param file_path: Path to the file
    :return:
    """
    new_path = f"{file_path}.jpg"

    video = cv2.VideoCapture(file_path)
    _, image = video.read()
    cv2.imwrite(new_path, image)

    return new_path


def get_anime_info(response: dict) -> str:
    """
    Get a ready-to-use info about an anime and return the whole text.

    :param response: JSON response
    :return:
    """
    japanese_title = html.escape(response["title_romaji"], False)
    english_title = html.escape(response["title_english"], False)
    episode = response["episode"]
    is_nsfw = "Yes" if response["is_adult"] else "No"

    if japanese_title == english_title:
        title_block = f"<b>Title:</b> <code>{japanese_title}</code>"
    else:
        title_block = (
            f"<b>English title:</b> <code>{english_title}</code>\n<b>Japanese title:</b> <code>{japanese_title}</code>"
        )

    if episode:
        minutes, seconds = divmod(int(response["at"]), 60)
        episode = f"\nEpisode <b>{episode}</b>, at <b>~{minutes:02d}:{seconds:02d}</b>"
    else:
        episode = ""

    anilist = ANILIST_URL.format(anime_id=response["anilist_id"])
    if response["mal_id"]:
        myanimelist = MAL_URL.format(anime_id=response["mal_id"])
        link_block = (
            f'<b><a href="{myanimelist}">Watch on MyAnimeList</a>\n<a href="{anilist}">Watch on Anilist</a></b>'
        )
    else:
        link_block = f'<b><a href="{anilist}">Watch on Anilist</a></b>'

    accuracy = (Decimal(response["similarity"]) * 100).quantize(Decimal(".01"))
    warn = ", <i>probably wrong</i>" if accuracy < 87 else ""
    full_text = f"{title_block}\n\nNSFW: <b>{is_nsfw}</b>\nAccuracy: <b>{accuracy}%</b>{warn}{episode}\n\n{link_block}"

    return full_text
