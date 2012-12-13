from game_engine import Game
from connection import Connection
from settings import Settings
import vkutils
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    connection_logger = logging.getLogger('connection')
    connection_logger.propagate = False
    connection_logger.addHandler(logging.FileHandler('connection.log'))
    unknownEventLogger = logging.getLogger('unknownEventLogger')
    unknownEventLogger.propagate = False
    unknownEventLogger.addHandler(logging.FileHandler('unknown_events.log'))

def read_params():
    settings = Settings()
    params = vkutils.VK(settings).getAppParams('612925')
    user_id = params['viewer_id']
    auth_key = params['auth_key']
    access_token = params['access_token']
    return (user_id, auth_key, access_token)

def run_game():
    setup_logging()
    (user_id, auth_key, access_token) = read_params()
    connection = Connection('http://java.shadowlands.ru/zombievk/go')
    Game(connection, user_id, auth_key, access_token).start()


if __name__ == '__main__':
    run_game()
