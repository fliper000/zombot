from game_engine import Game
from connection import Connection
from settings import Settings
import vkutils
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    params = vkutils.VK(settings).getAppParams('612925')
    user_id = params['viewer_id']
    auth_key = params['auth_key']
    access_token = params['access_token']
    connection = Connection('http://java.shadowlands.ru/zombievk/go')
    Game(connection, user_id, auth_key, access_token).start()
