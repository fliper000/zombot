from connection import Connection
from settings import Settings
import re
import json
class VK():
    def __init__(self, credentials):
        self._credentials = credentials

    def getAppParams(self, app_id):
        session_cookies = self._getSessionCookies()
        vk = Connection('http://vk.com/app' + str(app_id))
        html = vk.sendRequest(None, cookies=session_cookies)
        matcher = re.compile('.*var params = (.*);$')
        for line in html.split('\n'):
            match = matcher.match(line)
            if match is not None:
                params = match.group(1)
                break
        return json.loads(params)

    def _getSessionCookies(self):
        session_cookies = self._credentials.getSessionCookies()
        if session_cookies is None:
            #username = self.credentials.getUserName()
            #password = self.credentials.getPassword()
            pass
        return session_cookies

if __name__ == '__main__':
    credentials = Settings()
    vk = VK(credentials)
    print vk.getAppParams(612925)
