from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, RPCError, UserAdminInvalid
from pyrogram.types import ChatPermissions, Message

from utils import clean_up, parse_command


@Client.on_message(filters.me & filters.command('kick', prefixes='.') & filters.group)
async def kick(client: Client, message: Message):
    """
    Kick a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text('Send this command **in reply** or provide a **username/mention/ID**.')
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
                await message.edit_text('Cannot kick without **appropriate rights**.')
            except RPCError:
                await message.edit_text(f'Failed to kick {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command('ban', prefixes='.') & filters.group)
async def ban(client: Client, message: Message):
    """
    Ban a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message)
    if parse is None:
        await message.edit_text('Send this command **in reply** or provide a **username/mention/ID**.')
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
                await message.edit_text('Cannot ban without **appropriate rights**.')
            except RPCError:
                await message.edit_text(f'Failed to ban {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command('unban', prefixes='.') & filters.group)
async def unban(client: Client, message: Message):
    """
    Unban a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text('Send this command **in reply** or provide a **username/mention/ID**.')
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
                await message.edit_text('Cannot unban without **appropriate rights**.')
            except RPCError:
                await message.edit_text(f'Failed to unban {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command(['mute', 'ro'], prefixes='.') & filters.group)
async def mute(client: Client, message: Message):
    """
    Mute a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message)
    if parse is None:
        await message.edit_text('Send this command **in reply** or provide a **username/mention/ID**.')
    else:
        if parse.is_self:
            await message.edit_text('Cannot mute myself.')
        if parse.is_admin:
            await message.edit_text('Cannot mute admin.')
        else:
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_stickers=False,
                can_send_animations=False,
                can_send_games=False,
                can_send_polls=False
            )

            try:
                await message.chat.restrict_member(parse.user.id, permissions=permissions, until_date=parse.until_date)
                await message.edit_text(f'Muted {parse.user.mention} **{parse.text}**.')
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text('Cannot mute without **appropriate rights**.')
            except RPCError:
                await message.edit_text(f'Failed to mute {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)


@Client.on_message(filters.me & filters.command('unmute', prefixes='.') & filters.group)
async def unmute(client: Client, message: Message):
    """
    Unmute a user by their ID/username/mention or reply. Works only if you have appropriate rights.
    """
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text('Send this command **in reply** or provide a **username/mention/ID**.')
    else:
        if parse.is_self:
            await message.edit_text('Cannot unmute myself.')
        if parse.is_admin:
            await message.edit_text('Admin could not be muted.')
        if not parse.is_restricted:
            await message.edit_text(f'{parse.user.mention} is not muted.')
        else:
            permissions = ChatPermissions(  # We need all these perms to unmute *properly*
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

            try:
                await message.chat.restrict_member(parse.user.id, permissions=permissions)
                await message.edit_text(f'Unmuted {parse.user.mention}.')
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text('Cannot unmute without **appropriate rights**.')
            except RPCError:
                await message.edit_text(f'Failed to unmute {parse.user.mention}.')

    await clean_up(client, message.chat.id, message.message_id, 5)
