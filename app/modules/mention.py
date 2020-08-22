from pyrogram import Client, Filters, Message
from pyrogram.errors import RPCError


@Client.on_message(Filters.me & Filters.command('mention', prefixes='.'))
async def mention_handler(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) == 1:
        await message.edit_text(
            'Pass the username of the user you want to text-mention:\n`.mention @username.Any text(optional)`'
        )
    else:
        mention_parts = args[1].split('.', maxsplit=1)
        try:
            user = await client.get_users(mention_parts[0])
            user_name = f'{user.first_name} {user.last_name}' if user.last_name else user.first_name
            text = user_name if len(mention_parts) == 1 else mention_parts[1]
            link = f'<a href="tg://resolve?domain={user.username}">{text}</a>'
            if message.entities:
                for entity in message.entities:
                    if entity.type == 'bold':
                        link = f'<b>{link}</b>'
                    elif entity.type == 'italic':
                        link = f'<i>{link}</i>'
                    elif entity.type == 'strike':
                        link = f'<s>{link}</s>'

            await message.edit_text(link)
        except RPCError:
            await message.edit_text('The provided username is incorrect.')
