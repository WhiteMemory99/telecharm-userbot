from pathlib import Path
from typing import Any, Optional, Union

try:
    import ujson as json
except ImportError:
    import json


class JSONStorage:
    """JSON File storage to store user settings persistently."""

    def __init__(self, path: Optional[str] = None):
        if path:
            self.path = Path(path)
        else:
            self.path = Path(__file__).parent.parent / "files" / "user_settings.json"

        try:
            self.data: dict = self.read()
        except FileNotFoundError:
            with self.path.open("w"):
                self.data: dict = {}

    def read(self):
        with self.path.open("r") as file:
            try:
                return json.load(file)
            except ValueError:
                return {}

    def set(self, key: str, value: Union[str, int, bool]):
        self.data[key] = value

        with self.path.open("w") as file:
            return json.dump(self.data, file, indent=4)

    def get(self, key: str, default: Any = None):
        return self.data.get(key, default)
