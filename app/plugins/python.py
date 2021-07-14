import sys
import traceback
from io import StringIO

from pyrogram import filters

from app.utils import quote_html, Client, Message


@Client.on_message(filters.me & filters.command("py", prefixes="."))
async def execute_python(client: Client, message: Message):
    """
    Execute any Python 3 code. Native async code is unsupported,
    so import asyncio and run it manually whenever you need it.
    Note that the Client and Message are available for you here.
    """
    if args := message.get_args(maximum=1):
        clear_timeout = 20.5
        result_type = "Output"
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = StringIO()  # Replace stdout and stderr to catch prints and unhandled errors
            sys.stderr = StringIO()
            exec(args[0], globals(), locals())

            raw_output = sys.stdout.getvalue().strip().split("\n") if sys.stdout.getvalue() else None
            if raw_output:
                output = "\n".join(raw_output[:7])  # Limit the output length
                if len(raw_output) > 7:
                    output += "\n..."
            elif sys.stderr.getvalue():  # In case we have something in our stderr, we treat it as an error
                result_type = "Error log"
                output = sys.stderr.getvalue().strip()
            else:
                output = "The script was successful..."

            text = "<b>Input:</b>\n<pre>{}</pre>\n\n<b>{}:</b>\n<pre>{}</pre>".format(
                quote_html(args[0]), result_type, quote_html(output)
            )
        except Exception:
            etype, evalue, _ = sys.exc_info()
            text = "<b>Input:</b>\n<pre>{}</pre>\n\n<b>Error log:</b>\n<pre>{}</pre>".format(
                quote_html(args[0]),
                quote_html("".join(traceback.format_exception_only(etype, evalue)).strip()),  # A short message
            )
        finally:  # Always return to original stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    else:
        clear_timeout = 3.5
        text = "Write the <b>python code</b> to be executed."

    await message.edit_text(text, message_ttl=clear_timeout)
