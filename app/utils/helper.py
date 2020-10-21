import asyncio
import sys
from typing import Union

from pyrogram import Client
from pyrogram.errors import RPCError

from storage import json_settings


async def clean_up(client: Client, chat_id: Union[int, str], message_id: int, clear_after: int = 3.5) -> None:
    """
    Delete a message shortly after editing if cleaning up is enabled.

    :param client: Running pyrogram client
    :param chat_id: Chat ID
    :param message_id: Message ID
    :param clear_after: Time in seconds to wait before deleting
    :return:
    """
    if clear_after > 0 and json_settings.data.get('clean_up', False) is True:
        await asyncio.sleep(clear_after)
        try:
            await client.delete_messages(chat_id, message_id)
        except RPCError:
            return


def extract_entity_text(text: str, offset: int, length: int):
    """
    Get value of entity
    :param text: Full message text
    :param offset: Entity offset
    :param length: Entity length
    :return: Returns required part of the text
    """
    if sys.maxunicode == 0xffff:
        return text[offset:offset + length]

    entity_text = text.encode('utf-16-le')
    entity_text = entity_text[offset * 2:(offset + length) * 2]
    return entity_text.decode('utf-16-le')
