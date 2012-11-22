#from game_engine import Game
#from connection import Connection
from settings import Settings
import vkutils

if __name__ == '__main__':
    settings = Settings()
    params = vkutils.VK(settings).getAppParams('612925')
    user_id =  params['viewer_id']
    auth_key = params['auth_key']
    # connection = Connection('http://95.163.80.22/zombievk/go')
    # Game(connection, user_id, auth_key).start()
    print auth_key
    print user_id
