from pyrogram import Client, filters
from pyrogram.errors import FirstnameInvalid, FloodWait, UsernameInvalid, UsernameNotModified, UsernameOccupied
from pyrogram.types import Message

from app.utils import clean_up, get_args, quote_html


@Client.on_message(filters.me & filters.command("stats", prefixes="."))
async def stats(client: Client, message: Message):
    """
    Gather profile stats containing chats info to share it to anyone.
    """
    await message.edit_text("<i>Gathering info...</i>")
    user_list = []
    peak_unread_chat = None
    total_chats = channels = privates = groups = pinned = unread = peak_unread_count = bots = 0
    async for dialog in client.iter_dialogs():
        total_chats += 1
        if dialog.is_pinned:
            pinned += 1
        if dialog.unread_messages_count > 0:
            unread += 1
            if dialog.unread_messages_count > peak_unread_count:
                peak_unread_count = dialog.unread_messages_count
                peak_unread_chat = dialog.chat.title

        if dialog.chat.type == "channel":
            channels += 1
        elif dialog.chat.type in ("group", "supergroup"):
            groups += 1
        else:
            privates += 1
            user_list.append(dialog.chat.id)

    full_users = await client.get_users(user_list)
    for user in full_users:
        if user.is_bot:
            bots += 1

    contacts = await client.get_contacts_count()
    if peak_unread_chat:
        unread_data = f"<b>{peak_unread_count}</b> in <code>{quote_html(peak_unread_chat)}</code>"
    else:
        unread_data = f"<b>{peak_unread_count}</b>"

    await message.edit_text(
        f"Total chats: <b>{total_chats}</b>\nPinned: <b>{pinned}</b>\nUnread: <b>{unread}</b>\n"
        f"Channels: <b>{channels}</b>\nPrivates: <b>{privates}</b>\nBots: <b>{bots}</b>\nGroups: <b>{groups}</b>"
        f"\n\nTelegram contacts: <b>{contacts}</b>\nPeak value of unread per chat: {unread_data}"
    )
    await clean_up(client, message.chat.id, message.message_id, clear_after=20)


@Client.on_message(filters.me & filters.command("name", prefixes="."))
async def name(client: Client, message: Message):
    """
    Change profile name, this command is flexible and has an auto-balancer for long names.
    """
    args = get_args(message.text or message.caption, maximum=0)
    if not args:
        await message.edit_text("Pass your new name.\n<code>.name I'm a superman!</code>")
    else:
        if len(args) == 1:
            first_name = args[0][:64]
            last_name = ""
        elif len(args) == 2:
            first_name = args[0][:64]
            last_name = args[1][:64]
        else:  # A quite complex name specified, so we have to balance it a little
            divider = len(args) // 2
            first_name = " ".join(args[:divider])[:64]
            last_name = " ".join(args[divider:])[:64]

        try:
            await client.update_profile(first_name=first_name, last_name=last_name)
            result = f"{first_name} {last_name}" if last_name else first_name
            await message.edit_text(f"Your name's been changed to:\n<code>{quote_html(result)}</code>")
        except FirstnameInvalid:
            await message.edit_text("Your new first name is invalid.")
        except FloodWait as ex:
            await message.edit_text(f"<b>FloodWait</b>, retry in <code>{ex.x}</code> seconds.")

    await clean_up(client, message.chat.id, message.message_id)


@Client.on_message(filters.me & filters.command("username", prefixes="."))
async def username(client: Client, message: Message):
    """
    Change profile username. Supports "del" argument to delete the current username if there is one.
    """
    new_username = get_args(message.text or message.caption, maximum=1).lstrip("@")
    if not new_username:
        await message.edit_text("Pass your new username.\n<code>.username del</code> to delete it.")
    else:
        if new_username == "del":
            new_username = None
            text = "Your username's been deleted."
        else:
            text = f"Your username's been changed to:\n<code>@{quote_html(new_username)}</code>"

        try:
            await client.update_username(new_username)
            await message.edit_text(text)
        except UsernameNotModified:
            await message.edit_text("This username is not different from the current one.")
        except UsernameOccupied:
            await message.edit_text("This username is already taken.")
        except UsernameInvalid:
            if len(new_username) > 32:
                await message.edit_text("This username is too long.")
            else:
                await message.edit_text("This username is invalid.")
        except FloodWait as ex:
            await message.edit_text(f"<b>FloodWait</b>, retry in <code>{ex.x}</code> seconds.")

    await clean_up(client, message.chat.id, message.message_id)


@Client.on_message(filters.me & filters.command(["bio", "about"], prefixes="."))
async def bio(client: Client, message: Message):
    """
    Change about info block. Supports "del" argument to clear the current bio.
    """
    args = get_args(message.text or message.caption, maximum=1)
    if not args:
        await message.edit_text("Pass your new about info.\n<code>.bio del</code> to delete it.")
    else:
        if args == "del":
            args = ""
            text = "Your bio's been deleted."
        else:
            text = f"Your bio's been updated to:\n<code>{quote_html(args[:70])}</code>"

        try:
            await client.update_profile(bio=args[:70])  # Max bio length is 70 chars
            await message.edit_text(text)
        except FloodWait as ex:
            await message.edit_text(f"<b>FloodWait</b>, retry in <code>{ex.x}</code> seconds.")

    await clean_up(client, message.chat.id, message.message_id)
