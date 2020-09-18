from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import Message, User


@Client.on_message(filters.me & filters.command('mention', prefixes='.'))
async def mention_handler(client: Client, message: Message):
    """
    Mention a user in any chat by their username as in some Telegram clients.
    """
    args = message.text.partition(' ')[2]
    if not args:
        await message.edit_text(
            'Pass the username of the user you want to text-mention:\n`.mention @username.Any text(optional)`'
        )
    else:
        mention_parts = args.split('.', maxsplit=1)
        try:
            user: User = await client.get_users(mention_parts[0])
            text = None if len(mention_parts) == 1 else mention_parts[1]
            link = user.mention(text)
            if message.entities:  # Check if there's any styled text in the message.text and apply it
                for entity in message.entities:
                    if entity.type == 'bold':
                        link = f'<b>{link}</b>'
                    elif entity.type == 'italic':
                        link = f'<i>{link}</i>'
                    elif entity.type == 'strike':
                        link = f'<s>{link}</s>'

            await message.edit_text(link)
        except RPCError:
            await message.edit_text('Specified username is incorrect.')
