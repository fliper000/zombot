#!/usr/bin/python
# coding=utf-8
from game_engine import Game
from connection import Connection
from settings import Settings
import vkutils
import logging
import os
import errno
from user_interface import UserPrompt


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class MyLogger(logging.StreamHandler):

    def write(self, message):
      print message.decode('utf-8'),


def setup_logging(user_name):
    log_directory = 'logs/' + user_name
    mkdir_p(log_directory)
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT, stream=MyLogger())
    connection_logger = logging.getLogger('connection')
    connection_logger.propagate = False
    connection_logger.addHandler(
        logging.FileHandler(log_directory + '/connection.log')
    )
    unknownEventLogger = logging.getLogger('unknownEventLogger')
    unknownEventLogger.propagate = False
    unknownEventLogger.addHandler(
        logging.FileHandler(log_directory + '/unknown_events.log')
    )
    game_engine_logger = logging.getLogger('game_engine')
    game_engine_logger.propagate = False
    game_engine_logger.addHandler(
        logging.FileHandler(log_directory + '/game_engine.log')
    )


def get_vk():
    settings = Settings()
    users = settings.getUsers()
    selected_user = UserPrompt().prompt_user('Select user:', users)
    settings.setUser(selected_user)
    vk = vkutils.VK(settings)
    return vk


def run_game():
    vk = get_vk()
    params = vk.getAppParams('612925')
    user_id = params['viewer_id']
    auth_key = params['auth_key']
    access_token = params['access_token']

    setup_logging(str(user_id))
    connection = Connection('http://java.shadowlands.ru/zombievk/go')
    Game(connection, user_id, auth_key, access_token, UserPrompt(), vk=vk).start()


if __name__ == '__main__':
    run_game()
