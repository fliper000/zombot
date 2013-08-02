import ConfigParser
import logging


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
        return self.get_user_setting('session_cookies')

    def setSessionCookies(self, cookies_string):
        self.save_user_setting('session_cookies', cookies_string)

    def save_user_setting(self, setting_name, setting_value):
        self.parser.set(self._currentUser, setting_name, setting_value)
        with open(self.filename, 'w') as fp:
            self.parser.write(fp)

    def get_user_setting(self, setting_name):
        try:
            return self.parser.get(self._currentUser, setting_name)
        except ConfigParser.NoOptionError:
            return None

    def getUsers(self):
        return filter(lambda s: s != 'global_settings', self.parser.sections())

    def setUser(self, selected_user):
        self._currentUser = selected_user

    def get_ignore_errors(self):
        try:
            ignore_errors = self.parser.get('global_settings', 'ignore_errors')
            if (ignore_errors.lower() == 'true'):
                return True
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as _:
            pass
        return False

    def get_file_log_level(self):
        try:
            log_to_file = self.parser.get('global_settings', 'log_all')
            if (log_to_file.lower() == 'true'):
                return logging.INFO
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as _:
            pass
        return logging.ERROR
