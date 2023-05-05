import io
import pickle
import time
import linkedin_api.settings as settings


class Error(Exception):
    """Base class for other exceptions"""
    pass


class LinkedinSessionExpired(Error):
    pass


class CookieRepository(object):
    """
    Class to act as a repository for the cookies.
    """

    def __init__(self):
        self.cookies = {}

    def save(self, cookies, username):
        with io.BytesIO() as f:
            pickle.dump(cookies, f)
            f.seek(0)
            cookie_data = f.read()
        self.cookies[username] = cookie_data

    def get(self, username):
        cookies_data = self.cookies.get(username)
        if cookies_data:
            cookies = pickle.loads(cookies_data)
            if not CookieRepository._is_token_still_valid(cookies):
                raise LinkedinSessionExpired
            return cookies
        return None

    @staticmethod
    def _is_token_still_valid(cookiejar):
        _now = time.time()
        for cookie in cookiejar:
            if cookie.name == "JSESSIONID" and cookie.value:
                if cookie.expires and cookie.expires > _now:
                    return True
                break
        return False
