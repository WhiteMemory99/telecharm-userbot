from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message, User

from app.utils import clean_up, get_args


@Client.on_message(filters.me & filters.command('mention', prefixes='.'))
async def mention_command(client: Client, message: Message):
    """
    Mention a user in any chat by their username as in some Telegram clients.
    """
    args = get_args(message.text or message.caption, maximum=1)
    if not args:
        await message.edit_text(
            'Pass the username of the user you want to text-mention:\n`.mention @username.Any text(optional)`',
        )
        await clean_up(client, message.chat.id, message.message_id)
    else:
        mention_parts = args.split('.', maxsplit=1)
        try:
            user: User = await client.get_users(mention_parts[0])
            text = None if len(mention_parts) == 1 else mention_parts[1]
            link = user.mention(text)
            entities = message.entities or message.caption_entities
            if entities:  # Check if there's any styled text in the message.text and apply it
                for entity in entities:
                    if entity.type == 'bold':
                        link = f'<b>{link}</b>'
                    elif entity.type == 'italic':
                        link = f'<i>{link}</i>'
                    elif entity.type == 'strike':
                        link = f'<s>{link}</s>'

            await message.edit_text(link)
        except RPCError:
            await message.edit_text('Specified username is incorrect.')
            await clean_up(client, message.chat.id, message.message_id)
