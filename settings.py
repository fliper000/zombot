from ConfigParser import ConfigParser
class Settings():
    def __init__(self):
        self.parser = ConfigParser()
        self.parser.read('settings.ini')

    def getUserEmail(self):
        return self.parser.get('vk', 'user_email')

    def getUserPassword(self):
        return self.parser.get('vk', 'user_password')

    def getSessionCookies(self):
        return self.parser.get('vk', 'session_cookies')
