import inspect
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from aiographfix import Telegraph
from pydantic import BaseModel, validator
from pyrogram import filters
from pyrogram.filters import Filter
from pyrogram.handlers.handler import Handler

from app import SysInfo, __version__
from app.config import conf
from app.utils import Client, Message
from app.utils.decorators import doc_args


class HandlerData(BaseModel):
    commands: set
    custom_prefixes: Optional[set]
    description: str
    supported_args: Optional[List[tuple]]

    @validator("custom_prefixes")
    def filter_prefixes(cls, v):
        if v == {"."}:
            return None

        return v

    @property
    def readable_commands(self) -> str:
        return " / ".join(f"<b>{command}</b>" for command in self.commands)


def get_command_filter(filter_obj: Filter):
    """
    Filter is an object that stores other filters, they are nested.
    Hence, this recursion is used find and return the CommandFilter we need.
    """
    for value in filter_obj.__dict__.values():
        if type(value).__name__ == "CommandFilter":  # This filter is created at runtime
            return value
        elif isinstance(value, Filter):
            if result := get_command_filter(value):
                return result

    return None


def get_eligible_data(
    handlers: List[Handler],
) -> Tuple[Dict[str, List[HandlerData]], Dict[str, str]]:
    """Filter handlers and modules that contain docs and are not excluded and return them."""
    eligible_handlers = defaultdict(list)
    module_descriptions = {}
    for handler in handlers:
        if not handler.callback.__doc__ or getattr(handler.callback, "no_documentation", False):
            continue

        module_docstring = sys.modules[handler.callback.__module__].__doc__  # noqa
        module_name = handler.callback.__module__.split(".")[-1]  # noqa
        if module_docstring and not module_descriptions.get(module_name):
            module_descriptions[module_name] = inspect.cleandoc(module_docstring)

        if result := get_command_filter(handler.filters):
            eligible_handlers[module_name].append(
                HandlerData(
                    commands=result.commands,
                    custom_prefixes=result.prefixes,
                    description=inspect.cleandoc(handler.callback.__doc__),
                    supported_args=getattr(handler.callback, "documented_args", None),
                )
            )

    return eligible_handlers, module_descriptions


def prepare_page_content(handlers: List[Handler]) -> str:
    """Prepare the Telegraph page content based on the data we receive from Pyrogram dispatcher."""
    modules, module_descriptions = get_eligible_data(handlers)
    text_blocks = [
        f"<aside><p>Welcome to <b>Telecharm v{__version__}</b> - "
        "the mighty, speedy and cool Telegram userbot!\n"
        "This page is created and updated automatically and individually, based on your plugins."
        "\nCurrent number of installed and documented modules: "
        f"<b>{len(modules.keys())}</b>.</p></aside><hr />"
    ]
    for key, value in modules.items():
        text_blocks.append(f"<h3>{key.replace('_', ' ').capitalize()} module</h3>")

        # If module has __doc__, add it under the title
        if module_docs := module_descriptions.get(key):
            text_blocks.append(f"<p>{module_docs}</p><br />")

        module_content = []
        for handler in value:  # value contains list of HandlerData models
            if handler.supported_args:  # Command supports args (doc_args decorator)
                formatted_elements = []
                for arg in handler.supported_args:
                    joined = " | ".join(arg)
                    formatted_elements.append(f"<<i>{joined}</i>>")

                commands_args = "  " + " ".join(formatted_elements)
            else:
                commands_args = ""

            if handler.custom_prefixes:  # Command prefix is not (only) a dot
                prefixes = "".join(handler.custom_prefixes)
                prefixes = f"<p><i>This command has unusual prefixes:</i> {prefixes}</p>"
            else:
                prefixes = ""

            module_content.append(
                f"<blockquote>{handler.readable_commands}{commands_args}</blockquote>"
                f"{prefixes}<p>{handler.description}\n</p>"
            )

        text_blocks.append("".join(module_content) + "<hr />")

    text_blocks.append(
        "<p><i>Keep track of Telecharm development "
        f"progress on its <a href='{conf.github_url}'>GitHub</a> "
        "page, and thanks for choosing this userbot!</i></p>"
    )

    return "".join(text_blocks)


@Client.on_message(filters.me & filters.command(["help", "share"], prefixes="."))
@doc_args("nocache")
async def help_command(client: Client, message: Message):  # TODO: Add last time updated?
    """
    This command lets you access and update this page.
    Also, you can easily share telecharm this way,
    since it contains all the necessary info and links.

    By default, this guide is updated when either Telecharm version
    or number of registered commands has changed.
    To force an update, pass `<code>nocache</code>`.
    It might be useful when updating a single custom plugin.
    """
    no_cache = "nocache" in message.get_args()
    help_url = client.user_settings.get("help_current_url")
    last_version = client.user_settings.get("help_generation_version")
    last_handlers_number = client.user_settings.get("help_handlers_number")

    all_handlers: List[Handler] = []
    for group in client.dispatcher.groups.values():
        all_handlers += group

    handlers_number = len(all_handlers)
    if (
        no_cache
        or not help_url
        or last_version != __version__
        or last_handlers_number != handlers_number
    ):
        telegraph_token = client.user_settings.get("telegraph_access_token")
        telegraph = Telegraph(token=telegraph_token)
        if not telegraph_token:
            result = await telegraph.create_account("Telecharm service")
            client.user_settings.set("telegraph_access_token", result.access_token)

        page_title = "Telecharm Guide"
        content = prepare_page_content(all_handlers)
        if help_url:
            result = await telegraph.edit_page(help_url.split("/")[-1], page_title, content)
        else:
            result = await telegraph.create_page(page_title, content)

        help_url = result.url
        client.user_settings.set("help_current_url", result.url)
        client.user_settings.set("help_generation_version", __version__)
        client.user_settings.set("help_handlers_number", handlers_number)
        await telegraph.close()

    await message.edit_text(
        f"<b>Telecharm v{__version__}</b>:\n\nFast, simple and cool Telegram userbot."
        "\nIf you're a newbie, you can start with the auto-generated guide below."
        f'\n\n<i><a href="{help_url}">Telecharm Guide</a>'
        f'\n<a href="{conf.github_url}">Telecharm on GitHub</a></i>',
        disable_web_page_preview=True,
        message_ttl=30,
    )


@Client.on_message(filters.me & filters.command("sys", prefixes="."))
async def system_information(_, message: Message):
    """
    Show some technical info about the current system,
    used libraries` status, and Telecharm components.
    """
    await message.edit_text(str(SysInfo()), message_ttl=15)
