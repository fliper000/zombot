from connection import Connection
from settings import Settings
import re
import json
class VK():
    def __init__(self, credentials):
        self._credentials = credentials

    def getAppParams(self, app_id, session_cookies=None):
        if session_cookies is None:
            session_cookies = self._getSessionCookies()
        vk = Connection('http://vk.com/app' + str(app_id))
        html = vk.sendRequest(None, cookies=session_cookies)
        matcher = re.compile('.*var params = (.*);$')
        params = None
        for line in html.split('\n'):
            match = matcher.match(line)
            if match is not None:
                params = match.group(1)
                break
        if params is not None:
            return json.loads(params)
        return params

    def _validateSessionCookies(self, session_cookies):
        valid = False
        if session_cookies is not None:
            valid = self.getAppParams(1, session_cookies) is not None
        return valid

    def _getSessionCookies(self):
        session_cookies = self._credentials.getSessionCookies()
        cookies_are_valid = self._validateSessionCookies(session_cookies)
        if not cookies_are_valid:
            username = self._credentials.getUserEmail()
            password = self._credentials.getUserPassword()
            post = {'act':'login',
                    'role':'al_frame',
                    'expire':'',
                    'captcha_sid':'',
                    'captcha_key':'',
                    '_origin':'http://vk.com',
                    'email':username,
                    'pass':password}
            vk = Connection('http://login.vk.com/?act=login')
            session_cookies = vk.sendRequest(post, getCookies=True)
            session_cookies = ('Cookie:' +
                              session_cookies.output(attrs=[], header='', sep=';'))
            self._credentials.setSessionCookies(session_cookies)
        return session_cookies


if __name__ == '__main__':
    credentials = Settings()
    vk = VK(credentials)
    print vk.getAppParams(612925)
