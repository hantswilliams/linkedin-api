import io
import os
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

    TODO: refactor to use http.cookiejar.FileCookieJar
    """

    def __init__(self):
        self.cookies = {}

    def save(self, cookies, username):
        self._ensure_cookies_dir()
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

    def _ensure_cookies_dir(self):
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)

    def _get_cookies_filepath(self, username):
        """
        Return the absolute path of the cookiejar for a given username
        """
        return "{}{}.jr".format(self.cookies_dir, username)

    def _load_cookies_from_cache(self, username):
        cookiejar_filepath = self._get_cookies_filepath(username)
        try:
            with open(cookiejar_filepath, "rb") as f:
                cookies = pickle.load(f)
                return cookies
        except FileNotFoundError:
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
