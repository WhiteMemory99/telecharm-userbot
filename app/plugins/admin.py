from loguru import logger
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, FloodWait, RPCError, UserAdminInvalid
from pyrogram.types import ChatPermissions, Message

from app.utils import clean_up, parse_command, get_args


MUTE_PERMS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_stickers=False,
    can_send_animations=False,
    can_send_games=False,
    can_send_polls=False
)

UNMUTE_PERMS = ChatPermissions(  # We need all these perms to unmute *properly*
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_stickers=True,
    can_send_animations=True,
    can_send_games=True,
    can_send_polls=True,
    can_add_web_page_previews=True,
    can_invite_users=True,
    can_change_info=True,
    can_pin_messages=True,
    can_use_inline_bots=True
)


@Client.on_message(filters.me & filters.command('kick', prefixes='.') & filters.group)
async def kick(client: Client, message: Message):
    """
    Kick a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text('**Reply to message** or provide a valid **username/mention/ID**.')
    else:
        if parse.is_self:
            await message.edit_text('Cannot kick myself.')
        if parse.is_admin:
            await message.edit_text('Cannot kick admin.')
        if not parse.is_member:
            await message.edit_text(f'{parse.user.mention} is not a member of this group.')
        else:
            try:
                await message.chat.unban_member(parse.user.id)
                await message.edit_text(f'Kicked {parse.user.mention}.')
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text('Not enough rights to kick.')
            except RPCError as ex:
                logger.error(f'{ex} in .kick')
                await message.edit_text(f'Failed to kick {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command('ban', prefixes='.') & filters.group)
async def ban(client: Client, message: Message):
    """
    Ban a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message)
    if parse is None:
        await message.edit_text('**Reply to message** or provide a valid **username/mention/ID**.')
    else:
        if parse.is_self:
            await message.edit_text('Cannot ban myself.')
        if parse.is_admin:
            await message.edit_text('Cannot ban admin.')
        else:
            try:
                await message.chat.kick_member(parse.user.id, until_date=parse.until_date)
                await message.edit_text(f'Banned {parse.user.mention} **{parse.text}**.')
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text('Not enough rights to ban.')
            except RPCError as ex:
                logger.error(f'{ex} in .ban')
                await message.edit_text(f'Failed to ban {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command('unban', prefixes='.') & filters.group)
async def unban(client: Client, message: Message):
    """
    Unban a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text('**Reply to message** or provide a valid **username/mention/ID**.')
    else:
        if parse.is_self:
            await message.edit_text('Cannot unban myself.')
        if parse.is_admin:
            await message.edit_text('Admin could not be banned.')
        if not parse.is_kicked:
            await message.edit_text(f'{parse.user.mention} is not banned.')
        else:
            try:
                await message.chat.unban_member(parse.user.id)
                await message.edit_text(f'Unbanned {parse.user.mention}.')
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text('Not enough rights to unban.')
            except RPCError as ex:
                logger.error(f'{ex} in .unban')
                await message.edit_text(f'Failed to unban {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command(['mute', 'ro'], prefixes='.') & filters.group)
async def mute(client: Client, message: Message):
    """
    Mute a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message)
    if parse is None:
        await message.edit_text('**Reply to message** or provide a valid **username/mention/ID**.')
    else:
        if parse.is_self:
            await message.edit_text('Cannot mute myself.')
        if parse.is_admin:
            await message.edit_text('Cannot mute admin.')
        else:
            try:
                await message.chat.restrict_member(parse.user.id, permissions=MUTE_PERMS, until_date=parse.until_date)
                await message.edit_text(f'Muted {parse.user.mention} **{parse.text}**.')
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text('Not enough rights to mute.')
            except RPCError as ex:
                logger.error(f'{ex} in .mute')
                await message.edit_text(f'Failed to mute {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command(['unmute', 'unro'], prefixes='.') & filters.group)
async def unmute(client: Client, message: Message):
    """
    Unmute a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text('**Reply to message** or provide a valid **username/mention/ID**.')
    else:
        if parse.is_self:
            await message.edit_text('Cannot unmute myself.')
        if parse.is_admin:
            await message.edit_text('Admin could not be muted.')
        if not parse.is_restricted:
            await message.edit_text(f'{parse.user.mention} is not muted.')
        else:
            try:
                await message.chat.restrict_member(parse.user.id, permissions=UNMUTE_PERMS)
                await message.edit_text(f'Unmuted {parse.user.mention}.')
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text('Not enough rights to unmute.')
            except RPCError as ex:
                logger.error(f'{ex} in .unmute')
                await message.edit_text(f'Failed to unmute {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command('pin', prefixes='.') & filters.group)
async def pin(client: Client, message: Message):
    """
    Pin something by replying to it. Works only if you have appropriate rights.
    """
    if not message.reply_to_message:
        await message.edit_text('**Reply to the message** you want to pin.')
    else:
        full_chat = await client.get_chat(message.chat.id)  # Pinned message is only available through the request
        if full_chat.pinned_message and full_chat.pinned_message.message_id == message.reply_to_message.message_id:
            await message.edit_text('This message is already pinned.')
        else:
            args = get_args(message.text or message.caption)
            if 'loud' in args:
                status = 'loudly'
                is_silent = False
            else:
                status = 'silently'
                is_silent = True

            try:
                await client.pin_chat_message(
                    message.chat.id,
                    message.reply_to_message.message_id,
                    disable_notification=is_silent
                )
                await message.edit_text(f'Pinned the message **{status}**.')
            except ChatAdminRequired:
                await message.edit_text('Not enough rights to pin.')
            except FloodWait as ex:  # Pin has really strict limits
                await message.edit_text(f'**FloodWait**, retry in `{ex.x}` seconds.')
            except RPCError as ex:
                logger.error(f'{ex} in .pin')
                await message.edit_text('Failed to pin this message.')

    await clean_up(client, message.chat.id, message.message_id)


@Client.on_message(filters.me & filters.command('unpin', prefixes='.') & filters.group)
async def unpin(client: Client, message: Message):
    """
    Unpin the currently pinned message. Works only if you have appropriate rights.
    """
    full_chat = await client.get_chat(message.chat.id)  # Pinned message is only available through the request
    if full_chat.pinned_message is not None:
        args = get_args(message.text or message.caption)
        try:
            if 'all' in args:
                await client.unpin_all_chat_messages(message.chat.id)
                await message.edit_text('Unpinned all the pinned messages.')
            else:
                if message.reply_to_message:
                    await client.unpin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    await message.edit_text('Unpinned this message.')
                else:
                    await client.unpin_chat_message(message.chat.id, full_chat.pinned_message.message_id)
                    await message.edit_text('Unpinned the latest pinned message.')
        except ChatAdminRequired:
            await message.edit_text('Not enough rights to unpin.')
        except FloodWait as ex:  # Unpin has really strict limits
            await message.edit_text(f'**FloodWait**, retry in `{ex.x}` seconds.')
        except RPCError as ex:
            logger.error(f'{ex} in .unpin')
            await message.edit_text('Failed to unpin.')
    else:
        await message.edit_text('There is no any pinned message here.')

    await clean_up(client, message.chat.id, message.message_id)
