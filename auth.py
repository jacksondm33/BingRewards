import requests
import common as c
import time
from bs4 import BeautifulSoup
from random import randint
from http.cookiejar import Cookie


USE_SELF = object()


class Account:

    headers = c.headers
    cookies = requests.cookies.RequestsCookieJar()
    data = None
    proxies = c.proxies

    def __init__(self, email, password, mode):
        self.email = email
        self.password = password
        self.mode = mode

    def login(self, mobile=False, useProxy=False):
        if self.mode == "cookie":
            loginURL = self.preLogin(
                cookie=True, useProxy=useProxy)  # Login with cookie
            res = self.get(loginURL, useProxy=useProxy)
        else:
            postURL = self.preLogin(useProxy=useProxy)
            res = self.post(postURL, data=self.data, useProxy=useProxy)
        # Parse HTML Form
        form = BeautifulSoup(res.text, "html.parser").findAll("form")[
            0]  # Get Form
        params = dict()
        for field in form:
            params[field["name"]] = field["value"]  # Add each field to params
        self.headers["Host"] = c.host  # Set Host to Bing Server
        self.cookies.clear()
        res = self.post(form.get("action"), data=params, useProxy=useProxy)
        if mobile:
            self.headers = c.mobileHeaders

    def preLogin(self, cookie=False, useProxy=False):
        res = self.get(c.hostURL, useProxy=useProxy)
        # Get Login URL
        index = res.text.index("WindowsLiveId")  # Find URL
        cutText = res.text[index + 16:]  # Cut Text at Start of URL
        loginURL = cutText[:cutText.index("\"")]  # Cut at End of URL
        # Unescape URL
        loginURL = bytes(loginURL, encoding="UTF-8").decode("unicode_escape")
        # Get Login Cookies
        self.headers["Host"] = c.loginHost  # Set Host to Login Server
        res = self.get(loginURL, useProxy=useProxy)
        if cookie:
            self.cookies.set_cookie(self.getAuthCookie())  # Set Login Cookie
            return loginURL
        self.data = self.getAuthData()
        self.cookies["CkTst"] = "G" + \
            str(int(time.time() * 1000))  # Add Time Cookie
        # Get Post URL
        index = res.text.index(c.loginPostURL)  # Find URL
        cutText = res.text[index:]  # Cut Text at Start of URL
        postURL = cutText[:cutText.index("\'")]  # Cut at End of URL
        # Get PPFT
        index = res.text.index("sFTTag")  # Find PPFT
        cutText = res.text[index:]  # Cut Text Near PPFT
        PPFT = cutText[cutText.index(
            "value=") + 7:cutText.index("\"/>")]  # Cut PPFT
        self.data["PPFT"] = PPFT
        # Get PPSX
        index = res.text.index(",r:\'")  # Find PPSX
        cutText = res.text[index + 4:]  # Cut Text at Start of PPSX
        PPSX = cutText[:cutText.index("\'")]  # Cut at End of PPSX
        self.data["PPSX"] = PPSX
        # Finish Up
        self.cookies["wlidperf"] = "FR=L&ST=" + \
            str(int(time.time() * 1000))  # Add Another Time Cookie
        return postURL

    def logout(self):
        self.cookies.clear()

    def getAuthData(self):
        return {
            "login": self.email,
            "loginfmt": self.email,
            "passwd": self.password,
            "i13": "0",
            "type": "11",
            "LoginOptions": "3",
            "lrt": "",
            "ps": "2",
            "psRNGCDefaultType": "",
            "psRNGCEntropy": "",
            "psRNGCSLK": "",
            "canary": "",
            "ctx": "",
            "NewUser": "1",
            "FoundMSAs": "",
            "fspost": "0",
            "i21": "0",
            "i2": "1",
            "i17": "0",
            "i18": "__ConvergedLoginPaginatedStrings%7C1%2C__ConvergedLogin_PCore%7C1%2C",
            "i19": "2" + str(randint(0, 5000))
        }

    def getAuthCookie(self):
        return Cookie(
            version=0,
            name="PPAuth",
            value=self.password,
            port=None,
            port_specified=False,
            domain=".login.live.com",
            domain_specified=True,
            domain_initial_dot=False,
            path="/",
            path_specified=True,
            secure=False,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest=None
        )

    def request(self, method, URL, headers=USE_SELF, cookies=USE_SELF, params=None, data=None, proxies=USE_SELF, useProxy=False, setReferer=True, setCookies=True):
        headers = self.headers if headers is USE_SELF else headers
        cookies = self.cookies if cookies is USE_SELF else cookies
        proxies = self.proxies if proxies is USE_SELF else proxies
        res = requests.request(method, URL, headers=headers, cookies=cookies,
                               params=params, data=data, proxies=proxies if useProxy else None, verify=False)
        if setReferer:
            self.headers["Referer"] = URL
        if setCookies:
            self.cookies.update(res.cookies)
        return res

    def get(self, URL, headers=USE_SELF, cookies=USE_SELF, params=None, data=None, proxies=USE_SELF, useProxy=False, setReferer=True, setCookies=True):
        return self.request('GET', URL, headers, cookies, params, data, proxies, useProxy, setReferer, setCookies)

    def post(self, URL, headers=USE_SELF, cookies=USE_SELF, params=None, data=None, proxies=USE_SELF, useProxy=False, setReferer=True, setCookies=True):
        return self.request('POST', URL, headers, cookies, params, data, proxies, useProxy, setReferer, setCookies)
