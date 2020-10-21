import datetime
from dataclasses import dataclass
from typing import Optional, Tuple, Union

from pyrogram.errors import RPCError
from pyrogram.types import Message, User

from utils.helper import extract_entity_text


MODIFIERS = {
    "w": datetime.timedelta(weeks=1),
    "d": datetime.timedelta(days=1),
    "h": datetime.timedelta(hours=1),
    "m": datetime.timedelta(minutes=1),
    "s": datetime.timedelta(seconds=1)
}

MODIFIER_NAMES = {
    "w": 'week',
    "d": 'day',
    "h": 'hour',
    "m": 'minute',
    "s": 'second'
}


@dataclass
class CommandArgs:
    user: User
    until_date: int
    text: str
    is_self: bool = False
    is_admin: bool = False
    is_member: bool = False
    is_kicked: bool = False
    is_restricted: bool = False


async def parse_command(message: Message, with_time: bool = True) -> Optional[CommandArgs]:
    """
    Parse command arguments to extract user data, timedelta and other info.

    :param message: Message object containing a command
    :param with_time: True if you need to parse timedelta
    :return: Returns CommandArgs object on success
    """
    args = message.text.split()[1:]
    timedelta = datetime.timedelta(seconds=1)
    text = 'forever'

    if with_time:
        for data in args:
            if data[:-1].isdigit() and data[-1:].lower() in MODIFIERS.keys():
                timedelta, text = parse_timedelta(data)
                break

    if message.reply_to_message:
        return await build_args(message, message.reply_to_message.from_user.id, timedelta, text)

    entities = message.entities or message.caption_entities
    if entities:
        for entity in entities:  # Look for mentions or text mentions
            if entity.type == 'mention':
                username = extract_entity_text(message.text or message.caption, entity.offset, entity.length)
                return await build_args(message, username, timedelta, text)
            elif entity.type == 'text_mention':
                return await build_args(message, entity.user.id, timedelta, text)
        else:
            for item in args:  # Look for IDs in the split text
                if item.isdigit() and len(item) <= 12:
                    return await build_args(message, int(item), timedelta, text)

    return None


async def build_args(
        message: Message,
        user_id: Union[int, str],
        duration: datetime.timedelta,
        text: str) -> Optional[CommandArgs]:
    """
    Build a ready-to-use helper object to use in commands and get useful info.

    :param message: Message object
    :param user_id: Target user id or username
    :param duration: Command duration timedelta
    :param text: Command text based on the timedelta
    :return: Returns CommandArgs object on success
    """
    try:
        member = await message.chat.get_member(user_id)
        return CommandArgs(
            user=member.user,
            until_date=int((datetime.datetime.now() + duration).timestamp()),
            text=text,
            is_self=member.user.id == message.from_user.id,
            is_admin=member.status in ('administrator', 'creator'),
            is_member=member.is_member if member.status in ('restricted', 'kicked') else True,
            is_kicked=member.status == 'kicked',
            is_restricted=member.status == 'restricted',
        )
    except RPCError:
        return None


def parse_timedelta(data: str) -> Tuple[datetime.timedelta, str]:
    """
    Provide a ready-to-use timedelta extracted from a command text.

    :param data: Time value in format <number><modifier>
    :return: Returns Tuple on success
    """
    value, modifier = (int(data[:-1]), data[-1:].lower())
    try:
        duration = datetime.timedelta()
        duration += value * MODIFIERS[modifier]
        if duration <= datetime.timedelta(seconds=30):
            return datetime.timedelta(seconds=30), 'for 30 seconds'
        elif duration > datetime.timedelta(days=366):
            return duration, 'forever'
        else:
            if value > 1:
                word = MODIFIER_NAMES[modifier] + 's'
            else:
                word = MODIFIER_NAMES[modifier]

            return duration, f'for {value} {word}'
    except OverflowError:
        return datetime.timedelta(seconds=1), 'forever'
