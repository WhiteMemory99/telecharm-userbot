import asyncio
import sys
from typing import List, Union

from pyrogram import Client
from pyrogram.errors import RPCError

from app.storage import json_settings


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


def extract_entity_text(text: str, offset: int, length: int) -> str:
    """
    Get entity value.

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


def get_args(text: str, maximum: int = 2) -> Union[List[str], str]:
    """
    Get command arguments.

    :param text: Original text
    :param maximum: Maximum number of list items for split, 0 or less for unlimited.
    :return:
    """
    if maximum <= 0:
        maximum = -1
    elif maximum == 1:
        args = text.split(maxsplit=maximum)[1:]
        if args:
            return args[0]

        return args

    return text.split(maxsplit=maximum)[1:]
