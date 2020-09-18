from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

import config


@Client.on_message(filters.me & filters.command(['start', 'help'], prefixes='.'))
async def help_handler(_, message: Message):
    """
    Builtin help command to access command list.
    """
    args = message.text.split(maxsplit=2)
    if 'ru' in args:  # Russian version requested
        text = f'**Telecharm v{config.TELECHARM_VERSION}**:\n\n`.help` - Показать это сообщение.\n`.ping` - Текущий ' \
               f'пинг\n`.stats` - Статистика моего профиля.\n`.flood` - Флуд сообщениями.\n`.purge` - Очистка ' \
               f'сообщений\n`.name` - Сменить моё имя\n`.username` - Сменить мой юзернейм\n`.bio` - Отредактировать ' \
               f'"О себе"\n`.mention` - Текстовое упоминание\n`.resolve` - Проверить ID/Юзернейм/Приглашение\n\n' \
               f'__[Подробнее о командах]({config.GUIDE_LINK_RU})\n[Telecharm на GitHub]({config.GITHUB_LINK})__'
    else:  # English version requested
        text = f'**Telecharm v{config.TELECHARM_VERSION}**:\n`.help ru` for Russian\n\n`.help` - Show this message.\n' \
               f'`.ping` - Current ping\n`.stats` - My profile stats.\n`.flood` - Flood messages.\n`.purge` - Purge ' \
               f'messages\n`.name` - Change my name\n`.username` - Change my username\n`.bio` - Edit my about info\n' \
               f'`.mention` - Text mention\n`.resolve` - Resolve ID/Username/Invite link\n\n' \
               f'__[More on commands]({config.GUIDE_LINK_EN})\n[Telecharm on GitHub]({config.GITHUB_LINK})__'

    await message.edit_text(text, disable_web_page_preview=True)


@Client.on_message(filters.me & filters.command('ping', prefixes='.'))
async def ping_handler(_, message: Message):
    """
    Count the time it takes to process an update in ms.
    """
    start_time = datetime.now()
    await message.delete()
    duration = datetime.now() - start_time
    milliseconds = duration.microseconds / 1000
    await message.reply_text(f'Ping is **{milliseconds}ms**', quote=False)
