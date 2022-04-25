import sys
import traceback
from io import StringIO
from typing import Any

from pyrogram import Client, filters
from pyrogram.types import Message

from app.utils import quote_html
from app.utils.decorators import doc_args


@Client.on_message(filters.me & filters.command("py", prefixes="."))
@doc_args("code")
async def execute_python(client: Client, message: Message) -> Any:
    """
    Execute <s>almost</s> any Python 3 code.
    Native async code is unsupported, so import asyncio and run it manually whenever you need it.
    Note that the Client and Message <b>are available</b> for you in here.
    Also, be wary of security threats when using this command, and <b>DO NOT</b> use any suspicious
    code given by other people.
    """
    argument = " ".join(message.command[1:])
    if ".session" in argument:
        return await message.edit_text("This command was blocked due to security reasons.")

    if argument:
        result_type = "Output"
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            # Replace stdout and stderr to catch prints and unhandled errors
            sys.stdout = StringIO()
            sys.stderr = StringIO()
            exec(argument, globals(), locals())

            raw_output = (
                sys.stdout.getvalue().strip().split("\n") if sys.stdout.getvalue() else None
            )
            if raw_output:
                output = "\n".join(raw_output[:7])  # Limit the output length
                if len(raw_output) > 7:
                    output += "\n..."
            elif (
                sys.stderr.getvalue()
            ):  # In case we have something in our stderr, we treat it as an error
                result_type = "Error log"
                output = sys.stderr.getvalue().strip()
            else:
                output = "The script was successful..."

            text = "<b>Input:</b>\n<pre>{}</pre>\n\n<b>{}:</b>\n<pre>{}</pre>".format(
                quote_html(argument), result_type, quote_html(output)
            )
        except Exception:  # noqa
            ex_type, ex_value, _ = sys.exc_info()
            text = "<b>Input:</b>\n<pre>{}</pre>\n\n<b>Error log:</b>\n<pre>{}</pre>".format(
                quote_html(argument),
                quote_html("".join(traceback.format_exception_only(ex_type, ex_value)).strip()),
            )
        finally:  # Always return to original stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    else:
        text = "Write the <b>python code</b> to be executed."

    await message.edit_text(text)
