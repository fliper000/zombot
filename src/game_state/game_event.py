'''
Created on 28.11.2012

@author: john
'''
import json
from connection import Connection
import logging
from types import NoneType


def dict2obj(d, name=None):
        if isinstance(d, list):  # handle list
            if name:
                name = name.rstrip('s')
            d = [dict2obj(x, name) for x in d]
        if not isinstance(d, dict):  # handle simple types
            return d

        # d is dict, handle complex type
        if 'type' in d:
            class_name = d['type']
        elif 'cmd' in d:
            class_name = d['cmd'] + 'Command'
        elif name is not None:
            class_name = name
        else:
            class_name = 'UnknownObject'
        class_name = 'Game' + class_name[0].upper() + class_name[1:]
        if 'action' in d:
            base_class_name = 'GameAction'
            base_class = type(base_class_name, (object,), {})
        elif 'type' in d:
            base_class_name = 'GameType'
            base_class = type(base_class_name, (object,), {})
        elif 'item' in d:
            base_class_name = 'GameItem'
            base_class = type(base_class_name, (object,), {})
        else:
            base_class = object
        constructor = type(str(class_name), (base_class,), {})
        o = constructor()
        for k in d:
            o.__dict__[k] = dict2obj(d[k], k)
        return o


def obj2dict(obj):
    # handle list
    if isinstance(obj, list):
        d = [obj2dict(x) for x in obj]
    # handle simple types
    elif (isinstance(obj, str) or
          isinstance(obj, int) or
          isinstance(obj, unicode) or
          isinstance(obj, NoneType)):
        d = obj
    # handle dict
    elif isinstance(obj, dict):
        d = {}
        for key in obj:
            d[key] = obj2dict(obj[key])
    else:
        d = {}
        for key in obj.__dict__:
            d[key] = obj2dict(obj.__dict__[key])
    return d


class GameAction(object):
    def __init__(self, action):
        self.action = action


class GiftEvent(GameAction):

    def __init__(self, action, gift):
        super(GiftEvent, self).__init__(action)
        self.gift = gift
        self.type = 'gift'


class Gift(object):

    def __init__(self, gift_id):
        self.id = gift_id


class ApplyGiftEvent(GiftEvent):

    def __init__(self, gift):
        super(ApplyGiftEvent, self).__init__('applyGift', gift)


class GameItemReader():
    def __init__(self):
        self.content_dict = {}

    def get(self, item_id):
        item_id = str(item_id).lstrip('@')
        return self.content_dict[item_id]

    def read(self, filename):
        with open(filename) as f:
            self.contents = json.load(f)
        for content in self.contents:
            if 'id' not in content:
                logging.warn("there is no id:" + str(content))
            else:
                self.content_dict[content['id']] = content

    def download(self, filename):
        url = 'http://java.shadowlands.ru/zombievk/items'
        data = Connection(url).sendRequest({'lang': 'ru'})
        with open(filename, 'w') as f:
            f.write(data.encode('utf-8'))
