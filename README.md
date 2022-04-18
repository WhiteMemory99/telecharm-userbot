# **Telecharm userbot**

[![Python 3.8](https://img.shields.io/badge/Python-3.8%20or%20newer-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/47528bf391c9433ba5a0333c55f9f12a)](https://app.codacy.com/gh/WhiteMemory99/telecharm-userbot?utm_source=github.com&utm_medium=referral&utm_content=WhiteMemory99/telecharm-userbot&utm_campaign=Badge_Grade_Settings)  
A powerful, fast and simple Telegram userbot written in Python 3 and based on Pyrogram 1.X.
Currently, in active WIP state, so feel free to contribute.

## Starting up

**_Ensure you have installed the Python 3.8 or above before proceeding._**

### Preparations

1. Git clone this repo.

   ```cmd
   git clone https://github.com/WhiteMemory99/telecharm-userbot.git
   ```

2. Visit <https://my.telegram.org/apps> to get your own `api_id` and `api_hash`.
3. Rename `.env.dist` to `.env` and open it.
4. Edit `.env` file: fill in your `api_id`, `api_hash`.
5. **(Optional)** Visit [SauceNao](https://saucenao.com/user.php), log in and copy your API key
   to `saucenao_key`.  
   This is a must if you want to use the `.sauce` command.

### Docker deployment

**Make sure you have _[docker](https://docs.docker.com/get-docker/)_**.

1. Build the image. Choose **one** of the two options below.

- Basic image for everyone (**~210 MB**)

```cmd
docker build -t telecharm-image .
```

- Extended image with complete `.anime` capabilities (**~1.1 GB**)

```cmd
docker build -t telecharm-image -f Dockerfile.full .
```

2. After building, start the userbot in interactive mode.

```cmd
docker run -it -v userbot_data:/userbot/app/files --name telecharm telecharm-image
```

3. Enter your number, auth code from Telegram and 2FA password, if you have one.
4. Exit the interactive mode with **Ctrl+C** or any other combination, depends on your system.
5. Run the userbot with docker.

```cmd
docker start telecharm
```

### Poetry deployment

**_Make sure you have [poetry](https://python-poetry.org/docs/)._**

1. Install requirements.

   ```cmd
   poetry install
   ```

2. You can also install an optional **opencv-python** module to extend `.anime` functionality.

   ```cmd
   poetry install -E anime
   ```

3. Run the userbot with poetry.

   ```cmd
   poetry run python app
   ```

### Plain python deployment

1. Install dependencies.

   ```cmd
   pip install -r requirements.txt
   ```

2. If you want to extend `.anime` functionality, install an optional `opencv-python` module.

   ```cmd
   pip install opencv-python
   ```

3. Run the userbot.

   ```cmd
   python3 -m app
   ```

## Usage

Telecharm will automatically gather, generate and update documentation for all the commands you
have. No matter whether you use 3-rd party plugins or write them yourself. <br />At first launch,
send `.help` to any chat to create your personal guide page.

Thanks for using **Telecharm** :)

## Writing and using custom plugins

1. By convention, all custom plugins are supposed to go to `app/plugins/custom`.

2. Go to that folder and create a file named `example.py` as your first tutorial plugin.

3. Insert the code below into the file and read all the comments to understand how it works.

<details>
<summary>Look at the example code</summary>

```python
"""
app/plugins/custom/example.py
This text would also appear in Telecharm guide as a module description.
"""
import asyncio
from pyrogram import filters

from app.config import conf
from app.utils import Client, Message  # Use custom types for type-hinting
from app.utils.decorators import doc_exclude, doc_args


@Client.on_message(filters.me & filters.command("example", prefixes="."))
@doc_args("arg_name", ("date", "time"))  # Let the Telecharm guide know about supported args (OPTIONAL)
@doc_exclude  # This command will not appear in Telecharm guide, remove this line to check how the generation works :)
async def example_handler(client: Client, message: Message):
    """
    This text would appear in Telecharm guide along with the command if it wasn't excluded.

    You can even wrap it like that, or style with supported HTML texts like <b><i>THIS</b></i>.
    """
    await message.edit_text("Hey, this is the example of a custom plugin command.", message_ttl=0)
    # message_ttl is used for message clean up feature, so be sure to take it seriously.
    # For general and short replies you can leave it unfilled, so it will take the default TTL.
    # To disable TTL, pass 0 as the argument.

    if client.user_settings.get("clean_up"):  # You can access and alter user settings with client.user_settings
        await asyncio.sleep(1)
        await message.reply_text(
            "By the way, the clean up mode is on! So this message will disappear in 6 seconds.", message_ttl=6
        )
```

For more advanced usage, inspect my code and look at `app/utils`. <br />

</details>

4. That's basically all you need to do. You can restart Telecharm and use your new plugin. To
   update the guide, just send `.help` to any chat.