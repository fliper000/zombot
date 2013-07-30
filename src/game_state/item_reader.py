from game_state.game_event import dict2obj
import json
import logging
import os
import time
from connection import Connection
import pprint


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, obj, context, maxlevels, level):
        if isinstance(obj, unicode):
            return (obj.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, obj,
                                           context, maxlevels, level)


class GameItemReader():
    def __init__(self):
        self.content_dict = {}

    def get(self, item_id):
        item_id = str(item_id).lstrip('@')
        return dict2obj(self.content_dict[item_id])

    def get_name(self, item):
        return self.get(item.item).name

    def read(self, filename):
        with open(filename) as f:
            self.contents = json.load(f)
        for content in self.contents:
            if 'id' not in content:
                logging.warn("there is no id:" + str(content))
            else:
                self.content_dict[content['id']] = content

    def _getModificationTime(self, filename):
        try:
            return time.localtime(os.path.getmtime(filename))
        except OSError:  # no such file
            return None

    def download(self, filename):
        last_modified_time = self._getModificationTime(filename)
        url = 'http://java.shadowlands.ru/zombievk/items'
        data = Connection(url).getChangedDocument(
            data={'lang': 'ru'},
            last_client_time=last_modified_time
        )
        with open(filename, 'w') as f:
            f.write(data.encode('utf-8'))

    def pretty_write(self, filename):
        with open(filename, 'w') as f:
            pretty_dict = MyPrettyPrinter().pformat(self.content_dict)
            f.write(pretty_dict)

