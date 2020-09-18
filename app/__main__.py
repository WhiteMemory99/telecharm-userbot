from pyrogram import Client

import config


app = Client(  # TODO: Override the client for our needs
    session_name=config.USER_PHONE[1:],
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    phone_number=config.USER_PHONE,
)

if __name__ == '__main__':
    app.run()
