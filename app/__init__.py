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
            return 'json'

        return f'ujson {ujson.__version__}'
    
    @property
    def anime(self):
        try:
            import cv2
        except ImportError:
            return 'Limited'
        
        return 'Full'

    def collect(self):
        yield f'**{platform.python_implementation()}:** `{self.python}`'
        yield f'**System:** `{self.os}`'
        yield f'**pyrogram:** `{self.pyrogram}`'

        uvloop = self.uvloop
        yield f'**uvloop:** `{uvloop}`'

        json_mode = self.json_mode
        yield f'**JSON module:** `{json_mode}`'

        anime = self.anime
        yield f'**.anime features:** `{anime}`'

    def __str__(self):
        return '\n'.join(self.collect())
    
    
__version__ = '0.7.3'
