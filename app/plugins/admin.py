from loguru import logger
from pyrogram import filters
from pyrogram.errors import ChatAdminRequired, FloodWait, RPCError, UserAdminInvalid
from pyrogram.types import ChatPermissions

from app import config
from app.utils import parse_command, Client, Message

MUTE_PERMS = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_stickers=False,
    can_send_animations=False,
    can_send_games=False,
    can_send_polls=False,
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
    can_use_inline_bots=True,
)


@Client.on_message(filters.me & filters.command("kick", prefixes=".") & filters.group)
async def kick(_, message: Message):
    """Kick a user by their ID/username/mention or reply."""
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text("<b>Reply to message</b> or provide a valid <b>username/mention/ID</b>.", message_ttl=5)
    else:
        if parse.is_self:
            await message.edit_text("Cannot kick myself.", message_ttl=config.DEFAULT_TTL)
        if parse.is_admin:
            await message.edit_text("Cannot kick admin.", message_ttl=config.DEFAULT_TTL)
        if not parse.is_member:
            await message.edit_text(f"{parse.user.mention} is not a member of this group.", message_ttl=5)
        else:
            try:
                await message.chat.unban_member(parse.user.id)
                await message.edit_text(f"Kicked {parse.user.mention}.", message_ttl=5)
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text("Not enough rights to kick.", message_ttl=config.DEFAULT_TTL)
            except RPCError as ex:
                logger.error(f"{ex} in .kick")
                await message.edit_text(f"Failed to kick {parse.user.mention}.", message_ttl=5)


@Client.on_message(filters.me & filters.command("ban", prefixes=".") & filters.group)
async def ban(client: Client, message: Message):
    """Ban a user by their ID/username/mention or reply."""
    parse = await parse_command(message)
    if parse is None:
        await message.edit_text("<b>Reply to message</b> or provide a valid <b>username/mention/ID</b>.", message_ttl=5)
    else:
        if parse.is_self:
            await message.edit_text("Cannot ban myself.", message_ttl=config.DEFAULT_TTL)
        if parse.is_admin:
            await message.edit_text("Cannot ban admin.", message_ttl=config.DEFAULT_TTL)
        else:
            try:
                await message.chat.kick_member(parse.user.id, until_date=parse.until_date)
                await message.edit_text(f"Banned {parse.user.mention} <b>{parse.text}</b>.", message_ttl=7)

                if message.reply_to_message:
                    try:
                        await client.delete_messages(message.chat.id, message.reply_to_message.message_id)
                    except RPCError:
                        pass
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text("Not enough rights to ban.", message_ttl=config.DEFAULT_TTL)
            except RPCError as ex:
                logger.error(f"{ex} in .ban")
                await message.edit_text(f"Failed to ban {parse.user.mention}.", message_ttl=5)


@Client.on_message(filters.me & filters.command("unban", prefixes=".") & filters.group)
async def unban(_, message: Message):
    """Unban a user by their ID/username/mention or reply."""
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text("<b>Reply to message</b> or provide a valid <b>username/mention/ID</b>.", message_ttl=5)
    else:
        if parse.is_self:
            await message.edit_text("Cannot unban myself.", message_ttl=config.DEFAULT_TTL)
        if parse.is_admin:
            await message.edit_text("Admin could not be banned.", message_ttl=config.DEFAULT_TTL)
        if not parse.is_kicked:
            await message.edit_text(f"{parse.user.mention} is not banned.", message_ttl=5)
        else:
            try:
                await message.chat.unban_member(parse.user.id)
                await message.edit_text(f"Unbanned {parse.user.mention}.", message_ttl=5)
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text("Not enough rights to unban.", message_ttl=config.DEFAULT_TTL)
            except RPCError as ex:
                logger.error(f"{ex} in .unban")
                await message.edit_text(f"Failed to unban {parse.user.mention}.", message_ttl=5)


@Client.on_message(filters.me & filters.command(["mute", "ro"], prefixes=".") & filters.group)
async def mute(_, message: Message):
    """Mute a user by their ID/username/mention or reply."""
    parse = await parse_command(message)
    if parse is None:
        await message.edit_text("<b>Reply to message</b> or provide a valid <b>username/mention/ID</b>.", message_ttl=5)
    else:
        if parse.is_self:
            await message.edit_text("Cannot mute myself.", message_ttl=config.DEFAULT_TTL)
        if parse.is_admin:
            await message.edit_text("Cannot mute admin.", message_ttl=config.DEFAULT_TTL)
        else:
            try:
                await message.chat.restrict_member(parse.user.id, permissions=MUTE_PERMS, until_date=parse.until_date)
                await message.edit_text(f"Muted {parse.user.mention} <b>{parse.text}</b>.", message_ttl=7)
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text("Not enough rights to mute.", message_ttl=config.DEFAULT_TTL)
            except RPCError as ex:
                logger.error(f"{ex} in .mute")
                await message.edit_text(f"Failed to mute {parse.user.mention}.", message_ttl=5)


@Client.on_message(filters.me & filters.command(["unmute", "unro"], prefixes=".") & filters.group)
async def unmute(_, message: Message):
    """Unmute a user by their ID/username/mention or reply."""
    parse = await parse_command(message, with_time=False)
    if parse is None:
        await message.edit_text("<b>Reply to message</b> or provide a valid <b>username/mention/ID</b>.", message_ttl=5)
    else:
        if parse.is_self:
            await message.edit_text("Cannot unmute myself.", message_ttl=config.DEFAULT_TTL)
        if parse.is_admin:
            await message.edit_text("Admin could not be muted.", message_ttl=config.DEFAULT_TTL)
        if not parse.is_restricted:
            await message.edit_text(f"{parse.user.mention} is not muted.", message_ttl=5)
        else:
            try:
                await message.chat.restrict_member(parse.user.id, permissions=UNMUTE_PERMS)
                await message.edit_text(f"Unmuted {parse.user.mention}.", message_ttl=5)
            except (ChatAdminRequired, UserAdminInvalid):
                await message.edit_text("Not enough rights to unmute.", message_ttl=config.DEFAULT_TTL)
            except RPCError as ex:
                logger.error(f"{ex} in .unmute")
                await message.edit_text(f"Failed to unmute {parse.user.mention}.", message_ttl=5)


@Client.on_message(filters.me & filters.command("pin", prefixes=".") & filters.group)
async def pin(client: Client, message: Message):
    """Pin a message by replying to it."""
    if not message.reply_to_message:
        await message.edit_text("<b>Reply to the message</b> you want to pin.", message_ttl=config.DEFAULT_TTL)
    else:
        full_chat = await client.get_chat(message.chat.id)  # Pinned message is only available through the request
        if full_chat.pinned_message and full_chat.pinned_message.message_id == message.reply_to_message.message_id:
            await message.edit_text("This message is already pinned.", message_ttl=config.DEFAULT_TTL)
        else:
            if "loud" in message.get_args():
                status = "loudly"
                is_silent = False
            else:
                status = "silently"
                is_silent = True

            try:
                await client.pin_chat_message(
                    message.chat.id, message.reply_to_message.message_id, disable_notification=is_silent
                )
                await message.edit_text(f"Pinned the message <b>{status}</b>.", message_ttl=5)
            except ChatAdminRequired:
                await message.edit_text("Not enough rights to pin.", message_ttl=config.DEFAULT_TTL)
            except FloodWait as ex:  # Pin has really strict limits
                await message.edit_text(
                    f"<b>Too many requests</b>, retry in <code>{ex.x}</code> seconds.", message_ttl=5
                )
            except RPCError as ex:
                logger.error(f"{ex} in .pin")
                await message.edit_text("Failed to pin this message.", message_ttl=config.DEFAULT_TTL)


@Client.on_message(filters.me & filters.command("unpin", prefixes=".") & filters.group)
async def unpin(client: Client, message: Message):
    """Unpin the currently pinned message."""
    full_chat = await client.get_chat(message.chat.id)  # Pinned message is only available through the request
    if full_chat.pinned_message is not None:
        try:
            if "all" in message.get_args():
                await client.unpin_all_chat_messages(message.chat.id)
                await message.edit_text("Unpinned all the pinned messages.", message_ttl=config.DEFAULT_TTL)
            else:
                if message.reply_to_message:
                    await client.unpin_chat_message(message.chat.id, message.reply_to_message.message_id)
                    await message.edit_text("Unpinned this message.", message_ttl=config.DEFAULT_TTL)
                else:
                    await client.unpin_chat_message(message.chat.id, full_chat.pinned_message.message_id)
                    await message.edit_text("Unpinned the latest pinned message.", message_ttl=config.DEFAULT_TTL)
        except ChatAdminRequired:
            await message.edit_text("Not enough rights to unpin.", message_ttl=config.DEFAULT_TTL)
        except FloodWait as ex:  # Unpin has really strict limits
            await message.edit_text(f"<b>Too many requests</b>, retry in <code>{ex.x}</code> seconds.", message_ttl=5)
        except RPCError as ex:
            logger.error(f"{ex} in .unpin")
            await message.edit_text("Failed to unpin.", message_ttl=config.DEFAULT_TTL)
    else:
        await message.edit_text("There is no any pinned message here.", message_ttl=config.DEFAULT_TTL)
