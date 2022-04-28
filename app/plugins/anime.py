import re
from decimal import Decimal
from http.client import responses
from typing import Any, List, Optional

from aiohttp import ClientResponseError, ClientSession, ServerTimeoutError
from loguru import logger
from pydantic import BaseModel, Field, ValidationError, validator
from pyrogram import Client, __version__, filters
from pyrogram.types import Document, Message

from app.utils import quote_html

ALLOWED_MIME_TYPES = ("image", "video")

COUB_API_URL = "https://coub.com/api/v2/coubs/{}"
COUB_PATTERN = re.compile(r"(https?://)?(www\.)?coub\.com/view/(?P<video_id>[a-zA-Z\d]+)")


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
                romaji_text + f"\n<b>English title:</b> <code>"
                f"{self.anilist.title.english}</code>"
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


async def get_coub_first_frame_url(session: ClientSession, video_id: str) -> Optional[str]:
    """Get the first frame of a coub video. (640x360)"""
    try:
        async with session.get(
            COUB_API_URL.format(video_id),
            headers={"User-Agent": f"Telecharm/{__version__}"},
        ) as resp:
            resp.raise_for_status()
            coub_data = await resp.json()

        first_frame_raw_url = coub_data["picture"]
        return first_frame_raw_url.replace("%{version}", "med", 1)
    except ClientResponseError as ex:
        logger.error("Failed to get coub data: {}", ex)


@Client.on_message(filters.me & filters.command(["anime", "whatanime"], prefixes="."))
async def find_anime(client: Client, message: Message) -> Any:
    """
    Find anime source by replying to a photo, <b>image/video</b> document, GIF, video or coub URL.
    If successful, you will receive basic info about the found anime.

    Note, that <code>opencv-python</code> is required for GIF and video support.
    """
    target_msg = message.reply_to_message if message.reply_to_message else message
    media = target_msg.photo or target_msg.video or target_msg.animation or target_msg.document
    data = None

    session: ClientSession = getattr(client, "http_session")
    search_text = "<i>Contacting <b>TraceMoe</b>...</i>"
    if target_msg.text and (match := COUB_PATTERN.search(target_msg.text)):
        await message.edit_text(search_text)
        coub_first_frame_url = await get_coub_first_frame_url(session, match.group("video_id"))
        if not coub_first_frame_url:
            return await message.edit_text("Failed to retrieve this coub.")

        url = f"https://api.trace.moe/search?cutBorders&anilistInfo&url={coub_first_frame_url}"
    elif media is None or (
        isinstance(media, Document) and not media.mime_type.startswith(ALLOWED_MIME_TYPES)
    ):
        return await message.edit_text(
            "A photo, video, GIF, <b>image/video</b> document or coub URL is required.",
        )
    else:
        await message.edit_text(search_text)
        url = "https://api.trace.moe/search?cutBorders&anilistInfo"
        file = await client.download_media(target_msg, in_memory=True)
        file.seek(0)
        data = {"file": file}

    try:
        async with session.post(url, data=data) as resp:
            resp.raise_for_status()
            resp_json = await resp.json()
            parsed_result = AnimeResult.parse_obj(resp_json["result"][0])

        reply_to_id = message.reply_to_message.id if message.reply_to_message else None
        await client.send_video(
            message.chat.id,
            parsed_result.big_video_link,
            caption=parsed_result.format_to_text(),
            reply_to_message_id=reply_to_id,
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
        )
