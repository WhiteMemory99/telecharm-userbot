from typing import Union

from loguru import logger
from pyrogram import filters
from pyrogram.errors import (
    ChannelPrivate,
    InviteHashInvalid,
    PeerIdInvalid,
    RPCError,
    UsernameInvalid,
    UsernameNotOccupied,
)
from pyrogram.types import Chat, ChatPreview, User

from app.utils import Client, Message, quote_html
from app.utils.decorators import CHAT_IDENTIFIERS, doc_args

STATUS = {
    True: "Yes",
    False: "No",
}

DC_LOCATIONS = {
    1: "Miami",
    2: "Amsterdam",
    3: "Miami",
    4: "Amsterdam",
    5: "Singapore",
}


@Client.on_message(filters.me & filters.command(["resolve", "whois", "id"], prefixes="."))
@doc_args(CHAT_IDENTIFIERS)
async def resolve_command(client: Client, message: Message):
    """
    Get some information about a user, channel or group by specifying a proper identifier.
    If the target is a private group or channel,
    the information you receive will be <b>limited</b>.
    """
    info = None
    if entity := message.get_args(maximum=1):
        try:
            target: Chat = await client.get_chat(entity[0])
            if target.type == "private":  # Get a User object instead
                target: User = await client.get_users(target.id)

            info = get_entity_info(target)
        except (UsernameNotOccupied, UsernameInvalid):
            await message.edit_text("Wrong <b>username</b> specified.")
        except PeerIdInvalid:
            await message.edit_text("Wrong <b>ID</b> specified.")
        except InviteHashInvalid:
            await message.edit_text("Wrong <b>invitation link</b> specified.")
        except ChannelPrivate:
            await message.edit_text("Specified target cannot be accessed.")
        except RPCError as ex:
            logger.error(f"Could not resolve an entity due to {ex}")
            await message.edit_text("Specified argument is invalid.")
    else:
        if message.reply_to_message:  # It's a reply to another message
            if message.reply_to_message.from_user:
                info = get_entity_info(message.reply_to_message.from_user)
            elif message.reply_to_message.forward_from_chat:
                try:
                    info = get_entity_info(message.reply_to_message.forward_from_chat)
                except KeyError:
                    await message.edit_text(
                        f"Target <b>{message.reply_to_message.forward_from_chat.type}</b> "
                        f"cannot be accessed."
                    )
            else:
                await message.edit_text("Unable to resolve this message.")
        else:
            info = get_entity_info(message.from_user)

    if info:  # We successfully got the info
        await message.edit_text(info, disable_web_page_preview=True, message_ttl=20)


def get_entity_info(entity: Union[User, Chat, ChatPreview]) -> str:
    """
    Build info text according to a specified User or Chat object and return the result.

    :param entity: User/Chat/ChatPreview object of the target
    :return:
    """
    if isinstance(entity, User):  # It's a User object
        if entity.is_deleted:
            full_text = f"<b>{entity.first_name}</b>\n\nThis profile is deleted."
        else:
            dc_name = (
                f"{entity.dc_id}-{DC_LOCATIONS[entity.dc_id]}" if entity.dc_id else "Unavailable"
            )
            full_text = (
                f"<b>{entity.mention}</b>\n\n<b>ID</b>: "
                f"<code>{entity.id}</code>\nType: <b>user</b>\nIs bot: <b>"
                f"{STATUS[entity.is_bot]}</b>\nIs scam: "
                f"<b>{STATUS[entity.is_scam]}</b>\nData center: <b>{dc_name}</b>"
            )
    elif isinstance(entity, ChatPreview):  # It's a private chat preview
        full_text = (
            f"<b>{entity.title}</b>\n\nType: "
            f"<b>{entity.type}</b>\nIs private: <b>Yes</b>\n"
            f"Members count: <b>{entity.members_count}</b>"
            f"\n\n<i>Join this {entity.type} to get more info.</i>"
        )
    else:  # It's a Chat object
        dc_name = f"{entity.dc_id}-{DC_LOCATIONS[entity.dc_id]}" if entity.dc_id else "Unavailable"
        description = f"{quote_html(entity.description)}\n\n" if entity.description else ""
        linked_chat = (
            f"<code>{entity.linked_chat.id}</code>" if entity.linked_chat else "<b>None</b>"
        )
        is_private = not bool(entity.username)

        if entity.username:
            title = f'<a href="https://t.me/{entity.username}">{entity.title}</a>'
        else:
            title = quote_html(entity.title)

        full_text = (
            f"<b>{title}</b>\n\n{description}<b>ID</b>: "
            f"<code>{entity.id}</code>\nType: <b>{entity.type}</b>\n"
            f"Linked chat: {linked_chat}\nIs private: <b>{STATUS[is_private]}</b>\n"
            f"Is scam: <b>{STATUS[entity.is_scam]}</b>\nData center: <b>{dc_name}</b>"
        )

    return full_text
