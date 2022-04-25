from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message, User

from app.utils.decorators import doc_args


@Client.on_message(filters.me & filters.command("mention", prefixes="."))
@doc_args("username.optional text")
async def mention_command(client: Client, message: Message) -> None:
    """
    Generate mention link for a user by their username, as in some Telegram clients.
    This command lets you specify an <b>optional</b> custom text for the link.
    <b>For example:</b>
    `<code>.mention @username.Text That Would Appear Instead of User's Name</code>`.
    """
    argument = " ".join(message.command[1:])
    if not argument:
        await message.edit_text(
            "Pass the user you want to text-mention:\n"
            "<code>.mention @username.Optional text</code>",
        )
    else:
        mention_parts = argument.split(".", maxsplit=1)
        try:
            user: User = await client.get_users(mention_parts[0])
            text = None if len(mention_parts) == 1 else mention_parts[1]
            link = user.mention(text)

            entities = message.entities or message.caption_entities
            if entities:  # Check if there's any styled text in the message.text and applies it
                for entity in entities:
                    if entity.type == "bold":
                        link = f"<b>{link}</b>"
                    elif entity.type == "italic":
                        link = f"<i>{link}</i>"
                    elif entity.type == "strike":
                        link = f"<s>{link}</s>"

            await message.edit_text(link)
        except RPCError:
            await message.edit_text("Specified username is incorrect.")
