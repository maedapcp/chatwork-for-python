# -*- coding: utf-8 -*-

import logging
import requests

_url_me             = "https://api.chatwork.com/v1/me"
_url_my_status      = "https://api.chatwork.com/v1/my/status"
_url_my_tasks       = "https://api.chatwork.com/v1/my/tasks"
_url_rooms_members  = "https://api.chatwork.com/v1/rooms/{room_id:d}/members"
_url_rooms_messages = "https://api.chatwork.com/v1/rooms/{room_id:d}/messages" 


def auth(token):
    c = Client()
    c._token = token
    return c

class Client:
    _token = None
    _room_id = None
    _room_members = None

    def me(self):
        return self.__get(_url_me) 

    def my_status(self):
        return self.__get(_url_my_status)

    def my_tasks(self, **params):
        return self.__get(_url_my_tasks, params=params)

    def visit(self, room_id):
        self._room_id = room_id
        return self

    def members(self):
        self._room_members = {self._room_id: self.__get(_url_rooms_members.format(room_id=self._room_id))}
        return self._room_members[self._room_id]

    def post(self, body):
        return self.__post(_url_rooms_messages.format(room_id=self._room_id), params={"body": body})

    def post_to_all(self, body):
        if self._room_members is None or not self._room_members.has_key(self._room_id):
            self.members()
        body = "\n".join([u"[To:{}] {}さん".format(m["account_id"], m["name"]) for m in self._room_members[self._room_id]]) + "\n" + body.decode("utf-8")
        return self.post(body)

    def __get(self, url, **kwargs):
        response = requests.get(url, params=kwargs["params"] if kwargs.has_key("params") else None, headers={"X-ChatWorkToken": self._token})
        return self.__process_response(response)

    def __post(self, url, **kwargs):
        response = requests.post(url, params=kwargs["params"] if kwargs.has_key("params") else None, headers={"X-ChatWorkToken": self._token})
        return self.__process_response(response)

    def __process_response(self, response):
        logging.debug("url: {}".format(response.url))
        logging.debug("status_code: {}".format(response.status_code))
        logging.debug("encoding: {}".format(response.encoding))
        logging.debug("header: {}".format(response.headers))
        logging.debug("text: {}".format(response.text))
        return response.json() if response.status_code == 200 else None

