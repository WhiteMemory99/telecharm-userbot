from pyrogram import Client

import config


if __name__ == '__main__':
    Client(
        session_name=config.USER_PHONE[1:],
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        phone_number=config.USER_PHONE,
    ).run()
