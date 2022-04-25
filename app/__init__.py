import platform

import pyrogram


class SysInfo:
    @property
    def os(self):
        return platform.platform()

    @property
    def python(self):
        return platform.python_version()

    @property
    def pyrogram(self):
        return pyrogram.__version__

    @property
    def uvloop(self):
        try:
            import uvloop
        except ImportError:
            return

        return uvloop.__version__

    @property
    def json_mode(self):
        try:
            import ujson
        except ImportError:
            return "json"

        return f"ujson {ujson.__version__}"

    @property
    def anime(self):
        try:
            import cv2  # noqa
        except ImportError:
            return "Limited"

        return "Full"

    def collect(self):
        yield f"<b>{platform.python_implementation()}:</b> <code>{self.python}</code>"
        yield f"<b>System:</b> <code>{self.os}</code>"
        yield f"<b>pyrogram:</b> <code>{self.pyrogram}</code>"

        uvloop = self.uvloop
        yield f"<b>uvloop:</b> <code>{uvloop}</code>"

        json_mode = self.json_mode
        yield f"<b>JSON module:</b> <code>{json_mode}</code>"

        anime = self.anime
        yield f"<b>.anime features:</b> <code>{anime}</code>"

    def __str__(self):
        return "\n".join(self.collect())


__version__ = "2.0.0"
