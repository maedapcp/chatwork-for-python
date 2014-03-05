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
        return self._get(_url_me) 

    def my_status(self):
        return self._get(_url_my_status)

    def my_tasks(self, **payload):
        return self._get(_url_my_tasks, payload=payload)

    def visit(self, room_id):
        self._room_id = room_id
        return self

    def members(self):
        self._room_members = {self._room_id: self._get(_url_rooms_members.format(room_id=self._room_id))}
        return self._room_members[self._room_id]

    def post(self, body):
        """
        Post a message in this room.

        >>> auth('972608a5c871a0f76fac0e58f5c2871e').visit(17402654).post('test') is not None
        True
        """
        return self._post(_url_rooms_messages.format(room_id=self._room_id), payload={"body": body})

    def post_to_all(self, body):
        if self._room_members is None or "self._room_id" not in self._room_members:
            self.members()
        body = "\n".join([u"[To:{0}] {1}さん".format(m["account_id"], m["name"]) for m in self._room_members[self._room_id]]) + "\n" + body.decode("utf-8")
        return self.post(body)

    def _get(self, url, **kwargs):
        response = requests.get(url, params=kwargs["payload"] if "payload" in kwargs else None, headers={"X-ChatWorkToken": self._token})
        return self._process_response(response)

    def _post(self, url, **kwargs):
        response = requests.post(url, data=kwargs["payload"] if "payload" in kwargs else None, headers={"X-ChatWorkToken": self._token})
        return self._process_response(response)

    def _process_response(self, response):
        logging.debug("url: {0}".format(response.url))
        logging.debug("status_code: {0}".format(response.status_code))
        logging.debug("encoding: {0}".format(response.encoding))
        logging.debug("header: {0}".format(response.headers))
        logging.debug("text: {0}".format(response.text))
        return response.json() if response.status_code == 200 else None

