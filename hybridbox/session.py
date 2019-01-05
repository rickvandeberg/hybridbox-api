"""
    This file is part of hybridbox-api
    :copyright: (c) 2018 by Jakob Schreiner.
    :license: BSD, see LICENSE for more details.
"""

import requests
import base64
import hashlib
import re
import json


class Session(object):
    def __init__(self, username="admin", password="", ip="10.0.0.138"):
        self.USERNAME = username
        self.PASSWORD = password
        self.IP = ip
        self.session = requests.Session()
        self.csrf_param = ""
        self.csrf_token = ""

    def _encrypt_password(self):
        encrypted_password = self.USERNAME.encode("UTF-8") \
                             + base64.b64encode(hashlib.sha256(self.PASSWORD.encode("UTF-8"))
                                                .hexdigest().encode("UTF-8")) \
                             + self.csrf_param.encode("UTF-8") \
                             + self.csrf_token.encode("UTF-8")
        encrypted_password = str(hashlib.sha256(encrypted_password).hexdigest())
        return encrypted_password

    def _set_csrf(self, page):
        if type(page) == dict:
            self.csrf_param = page["csrf_param"]
            self.csrf_token = page["csrf_token"]
        elif page is not None:
            self.csrf_param = re.search('(.*csrf_param".{1,9})"(\w{32})"', page.text).group(2)
            self.csrf_token = re.search('(.*csrf_token".{1,9})"(\w{32})"', page.text).group(2)
        return 0

    @staticmethod
    def _get_json(given_string):
        json_string = re.search('(.*/\*)(.*)(\*/)', given_string).group(2)
        return json.loads(json_string)

    def _cleanup(self, r):
        try:
            json_response = self._get_json(r.text)
            self._set_csrf(json_response)
            return json_response["errcode"]
        except Exception as error:
            print("error: " + repr(error))

    def login(self):
        self.session = requests.Session()
        page = self.session.get("http://" + self.IP + "/html/index.html")
        if page.ok:
            self._set_csrf(page)
            encrypted_password = self._encrypt_password()
            csrf = dict(csrf_param=self.csrf_param, csrf_token=self.csrf_token)
            data = dict(UserName=self.USERNAME, Password=encrypted_password, LoginFlag=1)
            login_data = dict(csrf=csrf, data=data)
            r = self.session.post("http://" + self.IP + "/api/system/user_login", json=login_data)
            json_response = self._get_json(r.text)

            if json_response["errorCategory"] == "ok":
                self._set_csrf(json_response)
            else:
                raise Exception(json_response["errorCategory"])
            return self
        raise Exception("connection failed")

    def logout(self):
        csrf = dict(csrf_param=self.csrf_param, csrf_token=self.csrf_token)
        r = self.session.post("http://" + self.IP + "/api/system/user_logout", json=csrf)
        self.csrf_param = ""
        self.csrf_token = ""
        self.session.close()
        return self

    def turn5goff(self):
        csrf = dict(csrf_param=self.csrf_param, csrf_token=self.csrf_token)
        config5g = dict(enable="false", ID="InternetGatewayDevice.X_Config.Wifi.Radio.2.")
        data = dict(config5g=config5g)
        json_data = dict(action="BasicSettings", csrf=csrf, data=data)

        r = self.session.post("http://" + self.IP + "/api/ntwk/WlanBasic?showpass=false", json=json_data)
        return self._cleanup(r)

    def turn5gon(self):
        csrf = dict(csrf_param=self.csrf_param, csrf_token=self.csrf_token)
        config5g = dict(enable="true", ID="InternetGatewayDevice.X_Config.Wifi.Radio.2.")
        data = dict(config5g=config5g)
        json_data = dict(action="BasicSettings", csrf=csrf, data=data)

        r = self.session.post("http://" + self.IP + "/api/ntwk/WlanBasic?showpass=false", json=json_data)
        return self._cleanup(r)

    def turn2goff(self):
        csrf = dict(csrf_param=self.csrf_param, csrf_token=self.csrf_token)
        config2g = dict(enable="false", ID="InternetGatewayDevice.X_Config.Wifi.Radio.1.")
        data = dict(config5g=config2g)
        json_data = dict(action="BasicSettings", csrf=csrf, data=data)

        r = self.session.post("http://" + self.IP + "/api/ntwk/WlanBasic?showpass=false", json=json_data)
        return self._cleanup(r)

    def turn2gon(self):
        csrf = dict(csrf_param=self.csrf_param, csrf_token=self.csrf_token)
        config2g = dict(enable="true", ID="InternetGatewayDevice.X_Config.Wifi.Radio.1.")
        data = dict(config5g=config2g)
        json_data = dict(action="BasicSettings", csrf=csrf, data=data)

        r = self.session.post("http://" + self.IP + "/api/ntwk/WlanBasic?showpass=false", json=json_data)
        return self._cleanup(r)

