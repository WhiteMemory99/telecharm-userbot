import os
import tempfile
from decimal import Decimal
from http.client import responses
from typing import List, Optional

from aiohttp import ClientResponseError, ServerTimeoutError
from pydantic import BaseModel, Field, ValidationError, validator
from pyrogram import filters
from pyrogram.types import Animation, Document, Video

from app.utils import Client, Message, quote_html

try:
    import cv2
except ImportError:
    cv2 = None


class AnimeTitle(BaseModel):
    native: str
    romaji: str
    english: Optional[str]

    @validator("*")
    def secure_text(cls, v):
        if not v:
            return None

        return quote_html(v)


class AnilistData(BaseModel):
    id: int
    mal_id: int = Field(alias="idMal")
    title: AnimeTitle
    synonyms: List[str]
    is_adult: bool = Field(alias="isAdult")

    @validator("synonyms", each_item=True)
    def secure_text(cls, v):
        return f"<code>{quote_html(v)}</code>"


class AnimeResult(BaseModel):
    anilist: AnilistData
    filename: Optional[str]
    episode: Optional[int]
    from_time: Optional[float] = Field(alias="from")
    to_time: Optional[float] = Field(alias="to")
    similarity: float
    video: str
    image: str

    @validator("similarity")
    def normalize_similarity(cls, v):
        return (Decimal(v) * 100).quantize(Decimal(".01"))

    @property
    def big_video_link(self) -> str:
        return self.video + "&size=l"

    @property
    def title_block(self) -> str:
        romaji_text = f"<b>Japanese title:</b> <code>{self.anilist.title.romaji}</code>"
        if self.anilist.title.english:
            text = (
                romaji_text + f"\n<b>English title:</b> <code>{self.anilist.title.english}</code>"
            )
        else:
            text = romaji_text

        if self.anilist.synonyms:
            synonyms = ", ".join(self.anilist.synonyms)
            text += f"\n\n<b>Synonyms:</b> {synonyms}"

        return text

    @property
    def accuracy_status(self) -> str:
        if self.similarity > 97:
            return "fantastic"
        elif self.similarity > 91:
            return "great"
        elif self.similarity > 86:
            return "good"
        elif self.similarity > 80:
            return "bad"
        else:
            return "terrible"

    @property
    def tracking_links_block(self) -> str:
        anilist_url = f"https://anilist.co/anime/{self.anilist.id}"
        myanimelist_url = f"https://myanimelist.net/anime/{self.anilist.mal_id}"

        return (
            f'<b><a href="{myanimelist_url}">Track on MyAnimeList</a>\n'
            f'<a href="{anilist_url}">Track on Anilist</a></b>'
        )

    def format_to_text(self) -> str:
        """Format the API data into a human-readable state."""
        if self.episode:
            from_minutes, from_seconds = divmod(int(self.from_time), 60)
            to_minutes, to_seconds = divmod(int(self.to_time), 60)
            if from_minutes == to_minutes and from_seconds == to_seconds:
                time_code = f"at <b>{to_minutes:02d}:{to_seconds:02d}</b>"
            else:
                time_code = (
                    f"between <b>{from_minutes:02d}:{from_seconds:02d}</b> "
                    f"and <b>{to_minutes:02d}:{to_seconds:02d}</b>"
                )

            episode_text = f"\nEpisode <b>{self.episode}</b>, {time_code}"
        else:
            episode_text = ""

        is_nsfw = "Yes" if self.anilist.is_adult else "No"
        return (
            f"{self.title_block}\n\nNSFW: <b>{is_nsfw}</b>\n"
            f"Accuracy is <b>{self.accuracy_status}</b> - "
            f"{self.similarity}%{episode_text}\n\n{self.tracking_links_block}"
        )


@Client.on_message(filters.me & filters.command(["anime", "whatanime"], prefixes="."))
async def find_anime(client: Client, message: Message):  # TODO: Support video document?
    """
    Find anime source by replying to a photo, <b>image</b> document, GIF or video.
    If successful, you will receive basic info about the found anime.

    Note, that <code>opencv-python</code> is required for GIF and video support.
    """
    target_msg = message.reply_to_message if message.reply_to_message else message
    media = target_msg.photo or target_msg.video or target_msg.animation or target_msg.document

    if media is None or (isinstance(media, Document) and "image" not in media.mime_type):
        await message.edit_text(
            "A photo, video, GIF or <b>image</b> document is required.",
        )
    else:
        with tempfile.TemporaryDirectory() as tempdir:
            await message.edit_text("<i>Processing...</i>", message_ttl=0)
            file_path = await client.download_media(
                target_msg, file_name=os.path.join(tempdir, media.file_id)
            )
            if isinstance(media, (Animation, Video)):
                if cv2 is not None:
                    file_path = get_video_frame(file_path)
                else:
                    return await message.edit_text(
                        "This media type requires <code>opencv-python</code>.",
                    )

            try:
                async with await client.http_session.post(
                    "https://api.trace.moe/search?cutBorders&anilistInfo",
                    data={"file": open(file_path, "rb")},
                ) as resp:
                    resp.raise_for_status()
                    resp_json = await resp.json()
                    parsed_result = AnimeResult.parse_obj(resp_json["result"][0])

                if message.reply_to_message:
                    reply_to_id = message.reply_to_message.message_id
                else:
                    reply_to_id = None

                await client.send_video(
                    message.chat.id,
                    parsed_result.big_video_link,
                    caption=parsed_result.format_to_text(),
                    reply_to_message_id=reply_to_id,
                    message_ttl=35,
                )
                await message.delete()
            except ServerTimeoutError:
                await message.edit_text(
                    "Failed to get info about this anime:\n<code>Read Timeout</code>",
                )
            except ClientResponseError as ex:
                description = responses.get(ex.status)
                await message.edit_text(
                    f"Failed to get info about this anime:\n<code>{description}</code>",
                )
            except ValidationError:
                await message.edit_text(
                    "Seems that the API has changed.\n"
                    "Please, update Telecharm or wait for new versions.",
                    message_ttl=5,
                )


def get_video_frame(file_path: str) -> str:
    """
    Get a frame of any video or GIF with opencv. Requires opencv extras.

    :param file_path: Path to the file
    :return:
    """
    new_path = f"{file_path}.jpg"

    video = cv2.VideoCapture(file_path)  # noqa
    _, image = video.read()
    cv2.imwrite(new_path, image)  # noqa

    return new_path
