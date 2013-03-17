import ConfigParser


class Settings():
    def __init__(self, filename='settings.ini'):
        self.parser = ConfigParser.ConfigParser()
        self.parser.read(filename)
        self.filename = filename
        self._currentUser = None

    def getSite(self):
        try:
            return self.parser.get(self._currentUser, 'site')
        except ConfigParser.NoOptionError:
            return 'vk'


    def getUserEmail(self):
        return self.parser.get(self._currentUser, 'user_email')

    def getUserPassword(self):
        return self.parser.get(self._currentUser, 'user_password')

    def getSessionCookies(self):
        try:
            return self.parser.get(self._currentUser, 'session_cookies')
        except ConfigParser.NoOptionError:
            return None

    def setSessionCookies(self, cookies_string):
        self.parser.set(self._currentUser, 'session_cookies', cookies_string)
        with open(self.filename, 'w') as fp:
            self.parser.write(fp)

    def getUsers(self):
        return self.parser.sections()

    def setUser(self, selected_user):
        self._currentUser = selected_user
