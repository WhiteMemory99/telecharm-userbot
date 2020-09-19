from typing import Union

from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import (ChannelPrivate, InviteHashInvalid, PeerIdInvalid, RPCError, UsernameInvalid,
                             UsernameNotOccupied)
from pyrogram.types import Chat, Message, User

from modules import clean_up


STATUS = {
    True: 'Yes',
    False: 'No',
}

DC_LOCATIONS = {
    1: 'Miami',
    2: 'Amsterdam',
    3: 'Miami',
    4: 'Amsterdam',
    5: 'Singapore',
}


@Client.on_message(filters.me & filters.command(['resolve', 'whois'], prefixes='.'))
async def resolve_handler(client: Client, message: Message):
    """
    Resolve a ID/Username/Invite Link, works on both users and chats. Useful to quickly get info.
    """
    text = None
    entity = message.text.partition(' ')[2]
    if entity:  # Argument specified
        try:
            target: Chat = await client.get_chat(entity)
            if target.type == 'private':  # Get a User object instead
                target: User = await client.get_users(target.id)

            text = get_entity_info(target)
        except (UsernameNotOccupied, UsernameInvalid):
            await message.edit_text('Wrong **username** specified.')
        except PeerIdInvalid:
            await message.edit_text('Wrong **ID** specified.')
        except InviteHashInvalid:
            await message.edit_text('Wrong **invitation link** specified.')
        except ChannelPrivate:
            await message.edit_text('Specified target cannot be accessed.')
        except RPCError as ex:
            logger.error(f'Could not resolve an entity in {ex}')
            await message.edit_text('Specified argument is invalid.')
    else:  # Argument not specified
        if message.reply_to_message:  # It's a reply to another message
            if message.reply_to_message.from_user:
                text = get_entity_info(message.reply_to_message.from_user)
            elif message.reply_to_message.forward_from_chat:
                try:
                    text = get_entity_info(message.reply_to_message.forward_from_chat)
                except KeyError:
                    await message.edit_text(
                        f'Target **{message.reply_to_message.forward_from_chat.type}** cannot be accessed.'
                    )
            else:
                await message.edit_text('Unable resolve this message.')
        else:
            text = get_entity_info(message.from_user)

    if text:
        await message.edit_text(text, disable_web_page_preview=True)
        await clean_up(client, message.chat.id, message.message_id, clear_after=15)
    else:
        await clean_up(client, message.chat.id, message.message_id)


def get_entity_info(entity: Union[User, Chat]):
    """
    Build info text according to a specified User or Chat object and return the result.
    """
    dc_name = f'{entity.dc_id}-{DC_LOCATIONS[entity.dc_id]}' if entity.dc_id else 'Unavailable'

    if isinstance(entity, User):  # It's a User object
        if entity.is_deleted:
            full_text = f'**{entity.first_name}**\n\nThis profile is deleted.'
        else:
            full_text = f'**{entity.mention}**\n\n**ID**: `{entity.id}`\nType: **user**\nIs bot: **' \
                        f'{STATUS[entity.is_bot]}**\nIs scam: **{STATUS[entity.is_scam]}**\nData center: **{dc_name}**'
    else:  # It's a Chat object
        description = f'{entity.description}\n\n' if entity.description else ''
        linked_chat = f'`{entity.linked_chat.id}`' if entity.linked_chat else '**None**'
        is_private = True if not entity.username else False
        title = f'[{entity.title}](https://t.me/{entity.username})' if entity.username else entity.title

        full_text = f'**{title}**\n\n{description}**ID**: `{entity.id}`\nType: **{entity.type}**\n' \
                    f'Linked chat: {linked_chat}\nIs private: **{STATUS[is_private]}**\n' \
                    f'Is verified: **{STATUS[entity.is_verified]}**\nIs scam: **{STATUS[entity.is_scam]}**\n' \
                    f'Data center: **{dc_name}**'

    return full_text
