import asyncio
from typing import BinaryIO, Coroutine, List, Optional, Union

from aiohttp import ClientSession
from pyrogram import Client as PyrogramClient
from pyrogram.errors import RPCError
from pyrogram.types import ForceReply, InlineKeyboardMarkup
from pyrogram.types import Message as PyrogramMessage
from pyrogram.types import MessageEntity, ReplyKeyboardMarkup, ReplyKeyboardRemove
from saucenaopie import AsyncSauceNao

from app.storage.json_storage import JSONStorage


class Client(PyrogramClient):
    def __init__(
        self, saucenao: Optional[AsyncSauceNao], default_ttl: Union[int, float], *args, **kwargs
    ) -> None:
        self.user_settings = JSONStorage()
        self.http_session = ClientSession(read_timeout=10.0)
        self.saucenao = saucenao
        self.default_ttl = default_ttl
        super().__init__(*args, **kwargs)

    def stop(self, block: bool = True) -> Coroutine:
        self.loop.run_until_complete(self.http_session.close())
        return super().stop(block=block)

    async def clean_up(
        self, chat_id: Union[int, str], message_id: int, message_ttl: Union[int, float]
    ) -> None:
        if self.user_settings.get("clean_up"):
            await asyncio.sleep(message_ttl)
            try:
                await self.delete_messages(chat_id, message_id)
            except RPCError:
                return

    async def edit_message_text(
        self,
        chat_id: Union[int, str],
        message_id: int,
        text: str,
        parse_mode: Optional[str] = object,
        entities: List["MessageEntity"] = None,
        disable_web_page_preview: bool = None,
        reply_markup: "InlineKeyboardMarkup" = None,
        message_ttl: Optional[Union[int, float]] = None,
    ) -> "Message":
        if message_ttl is None:
            message_ttl = self.default_ttl

        if message_ttl:
            asyncio.create_task(self.clean_up(chat_id, message_id, message_ttl))

        return await super().edit_message_text(
            chat_id, message_id, text, parse_mode, entities, disable_web_page_preview, reply_markup
        )

    async def send_video(
        self,
        chat_id: Union[int, str],
        video: Union[str, BinaryIO],
        caption: str = "",
        parse_mode: Optional[str] = object,
        caption_entities: List["MessageEntity"] = None,
        ttl_seconds: int = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: Union[str, BinaryIO] = None,
        file_name: str = None,
        supports_streaming: bool = True,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: int = None,
        reply_markup: Union[
            "InlineKeyboardMarkup", "ReplyKeyboardMarkup", "ReplyKeyboardRemove", "ForceReply"
        ] = None,
        progress: callable = None,
        progress_args: tuple = (),
        message_ttl: Optional[Union[int, float]] = None,
    ) -> Optional["Message"]:
        sent_message = await super().send_video(
            chat_id,
            video,
            caption,
            parse_mode,
            caption_entities,
            ttl_seconds,
            duration,
            width,
            height,
            thumb,
            file_name,
            supports_streaming,
            disable_notification,
            reply_to_message_id,
            schedule_date,
            reply_markup,
            progress,
            progress_args,
        )

        if message_ttl is None:
            message_ttl = self.default_ttl

        if message_ttl:
            asyncio.create_task(self.clean_up(chat_id, sent_message.message_id, message_ttl))

        return sent_message

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = object,
        entities: List["MessageEntity"] = None,
        disable_web_page_preview: bool = None,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: int = None,
        reply_markup: Union[
            "InlineKeyboardMarkup", "ReplyKeyboardMarkup", "ReplyKeyboardRemove", "ForceReply"
        ] = None,
        message_ttl: Optional[Union[int, float]] = None,
    ) -> "Message":
        sent_message = await super().send_message(
            chat_id,
            text,
            parse_mode,
            entities,
            disable_web_page_preview,
            disable_notification,
            reply_to_message_id,
            schedule_date,
            reply_markup,
        )

        if message_ttl is None:
            message_ttl = self.default_ttl

        if message_ttl:
            asyncio.create_task(self.clean_up(chat_id, sent_message.message_id, message_ttl))

        return sent_message


class Message(PyrogramMessage):
    _client: Client

    async def edit_text(
        self,
        text: str,
        parse_mode: Optional[str] = object,
        entities: List["MessageEntity"] = None,
        disable_web_page_preview: bool = None,
        reply_markup: "InlineKeyboardMarkup" = None,
        message_ttl: Optional[Union[int, float]] = None,
    ) -> "Message":
        return await self._client.edit_message_text(
            chat_id=self.chat.id,
            message_id=self.message_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup,
            message_ttl=message_ttl,
        )

    async def reply_text(
        self,
        text: str,
        quote: bool = None,
        parse_mode: Optional[str] = object,
        entities: List["MessageEntity"] = None,
        disable_web_page_preview: bool = None,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        reply_markup=None,
        message_ttl: Optional[Union[int, float]] = None,
    ) -> "Message":
        if quote is None:
            quote = self.chat.type != "private"

        if reply_to_message_id is None and quote:
            reply_to_message_id = self.message_id

        return await self._client.send_message(
            chat_id=self.chat.id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_web_page_preview=disable_web_page_preview,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            message_ttl=message_ttl,
        )

    def get_args(self, maximum: int = -1) -> List[str]:
        text = self.text or self.caption
        if not text:
            raise ValueError("This message doesn't have any text.")

        if maximum <= 0:
            maximum = -1

        return text.split(maxsplit=maximum)[1:]
