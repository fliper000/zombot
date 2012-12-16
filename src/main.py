from game_engine import Game
from connection import Connection
from settings import Settings
import vkutils
import logging
import os
import errno


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def setup_logging(user_name):
    log_directory = 'logs/' + user_name
    mkdir_p(log_directory)
    logging.basicConfig(level=logging.INFO)
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


def select_user(users):
    prompt_string = "\n".join([str(index + 1) + ": " + user
                               for index, user in enumerate(users)])
    selected_user_index = -1
    while not selected_user_index in range(len(users)):
        try:
            selected_user_index = int(raw_input(prompt_string + "\n")) - 1
        except ValueError:
            pass
    selected_user = users[selected_user_index]
    print "You selected " + selected_user
    return selected_user


def read_params():
    settings = Settings()
    users = settings.getUsers()
    selected_user = select_user(users)
    settings.setUser(selected_user)
    params = vkutils.VK(settings).getAppParams('612925')
    user_id = params['viewer_id']
    auth_key = params['auth_key']
    access_token = params['access_token']
    return (user_id, auth_key, access_token)


def run_game():
    (user_id, auth_key, access_token) = read_params()
    setup_logging(str(user_id))
    connection = Connection('http://java.shadowlands.ru/zombievk/go')
    Game(connection, user_id, auth_key, access_token).start()


if __name__ == '__main__':
    run_game()
