import pathlib
from typing import Union

import ujson


class JSONStorage:
    """
    JSON File storage to store user settings persistently.
    """

    def __init__(self, path: str):
        self.path = pathlib.Path(path)
        try:
            self.data: dict = self.read()
        except FileNotFoundError:
            with self.path.open('w'):
                self.data: dict = {}

    def read(self):
        with self.path.open('r') as file:
            try:
                return ujson.load(file)
            except ValueError:
                return {}

    def write(self, key: str, value: Union[str, int, bool]):
        self.data[key] = value

        with self.path.open('w') as file:
            return ujson.dump(self.data, file, indent=4)


jstorage = JSONStorage('app/storage/storage.json')  # We insert the path to our JSON storage, created automatically
