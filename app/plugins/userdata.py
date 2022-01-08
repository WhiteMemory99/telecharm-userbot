from pyrogram import filters
from pyrogram.errors import (
    FirstnameInvalid,
    FloodWait,
    UsernameInvalid,
    UsernameNotModified,
    UsernameOccupied,
)

from app.utils import Client, Message, quote_html
from app.utils.decorators import doc_args


@Client.on_message(filters.me & filters.command("stats", prefixes="."))
async def gather_stats(client: Client, message: Message):  # TODO: Improve stats
    """
    Get some interesting statistics on your chats and profile.
    <i>This command shows the most unread chat,
    so beware of leaking some shameful stuff to others</i> xD
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
        f"Total chats: <b>{total_chats}</b>\nPinned: <b>{pinned}</b>\n"
        f"Unread: <b>{unread}</b>\nChannels: <b>{channels}</b>\nPrivates: <b>{privates}</b>\n"
        f"Bots: <b>{bots}</b>\nGroups: <b>{groups}</b>\n\n"
        f"Telegram contacts: <b>{contacts}</b>\nPeak value of unread per chat: {unread_data}",
        message_ttl=25,
    )


@Client.on_message(filters.me & filters.command("name", prefixes="."))
@doc_args("name")
async def change_name(client: Client, message: Message):
    """
    Change the profile first name and/or last name,
    this command is flexible and has auto-balancing for long and messy names.
    The text length limit is <b>128</b>, the rest will be cut.
    """
    args = message.get_args()
    if not args:
        await message.edit_text("Pass your new name.\n<code>.name I'm a superman!</code>")
    else:
        if len(args) == 1:
            first_name = args[0][:64]
            last_name = ""
        elif len(args) == 2:
            first_name = args[0][:64]
            last_name = args[1][:64]
        else:  # Quite a complex name specified, so we have to balance it a little
            divider = len(args) // 2
            first_name = " ".join(args[:divider])[:64]
            last_name = " ".join(args[divider:])[:64]

        try:
            await client.update_profile(first_name=first_name, last_name=last_name)
            full_name = f"{first_name} {last_name}" if last_name else first_name
            await message.edit_text(
                f"Your name's been changed to:\n<code>{quote_html(full_name)}</code>",
                message_ttl=5,
            )
        except FirstnameInvalid:
            await message.edit_text("Your new first name is invalid.")
        except FloodWait as ex:
            await message.edit_text(
                f"<b>Too many requests</b>, retry in <code>{ex.x}</code> seconds.", message_ttl=5
            )


@Client.on_message(filters.me & filters.command("username", prefixes="."))
@doc_args("username")
async def change_username(client: Client, message: Message):
    """
    Change the profile username. The text length limit is <b>32</b>.
    Supports `<code>del</code>` argument to delete the current username, if there is one.
    """
    args = message.get_args(maximum=1)
    if not args:
        await message.edit_text(
            "Pass your new username.\n<code>.username del</code> to delete it."
        )
    else:
        new_username = args[0].lstrip("@")
        if new_username == "del":
            new_username = None
            text = "Your username's been deleted."
        else:
            text = f"Your username's been changed to:\n<code>@{quote_html(new_username)}</code>"

        try:
            await client.update_username(new_username)
            await message.edit_text(text, message_ttl=5)
        except UsernameNotModified:
            await message.edit_text("This username is not different from the current one.")
        except UsernameOccupied:
            await message.edit_text("This username is taken.")
        except UsernameInvalid:
            if len(new_username) > 32:
                await message.edit_text("This username is too long.")
            else:
                await message.edit_text("This username is invalid.")
        except FloodWait as ex:
            await message.edit_text(
                f"<b>Too many requests</b>, retry in <code>{ex.x}</code> seconds.", message_ttl=5
            )


@Client.on_message(filters.me & filters.command(["bio", "about"], prefixes="."))
@doc_args("text")
async def change_bio(client: Client, message: Message):
    """
    Change the profile about block. The text length limit is <b>70</b>, the rest will be cut.
    Supports `<code>del</code>` argument to delete the current bio, if there is one.
    """
    args = message.get_args(maximum=1)
    if not args:
        await message.edit_text("Pass your new about info.\n<code>.bio del</code> to delete it.")
    else:
        new_bio = args[0]
        if new_bio == "del":
            new_bio = ""
            text = "Your bio's been deleted."
        else:
            me = await client.get_me()
            me_chat = await client.get_chat(me.id)
            if me_chat.bio == new_bio:
                return await message.edit_text("This text is no different from your current bio.")

            text = f"Your bio's been updated to:\n<code>{quote_html(new_bio[:70])}</code>"

        try:
            # Max bio length is 70 chars, so we`ll cut it
            await client.update_profile(bio=new_bio[:70])
            await message.edit_text(text, message_ttl=10)
        except FloodWait as ex:
            await message.edit_text(
                f"<b>Too many requests</b>, retry in <code>{ex.x}</code> seconds.", message_ttl=5
            )
