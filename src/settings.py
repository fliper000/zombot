import ConfigParser


class Settings():
    def __init__(self, filename='settings.ini'):
        self.parser = ConfigParser.ConfigParser()
        self.parser.read(filename)
        self.filename = filename

    def getUserEmail(self):
        return self.parser.get('vk', 'user_email')

    def getUserPassword(self):
        return self.parser.get('vk', 'user_password')

    def getSessionCookies(self):
        try:
            return self.parser.get('vk', 'session_cookies')
        except ConfigParser.NoOptionError:
            return None

    def setSessionCookies(self, cookies_string):
        self.parser.set('vk', 'session_cookies', cookies_string)
        with open(self.filename, 'w') as fp:
            self.parser.write(fp)
