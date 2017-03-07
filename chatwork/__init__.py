# -*- coding: utf-8 -*-

try:
    # python2
    unicode

    def u(str):
        return str.decode("utf-8")

    def b(str):
        return str
except:
    # python3
    def u(str):
        return str

    def b(str):
        return str.encode("utf-8")

from easydict import EasyDict

import logging
import requests

_url_me = 'https://api.chatwork.com/v1/me'

_url_my_status = 'https://api.chatwork.com/v1/my/status'

_url_my_tasks = 'https://api.chatwork.com/v1/my/tasks'

_url_rooms_members = 'https://api.chatwork.com/v1/rooms/{room_id:d}/members'

_url_rooms_messages = 'https://api.chatwork.com/v1/rooms/{room_id:d}/messages'


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class VagabondError(Error):
    def __str__(self):
        return 'Not visit the room yet.'


class VeryHardError(Error):
    def __str__(self):
        return 'That obj is very hard not easy.'


def _to_easy(obj):
    if isinstance(obj, (list, tuple)):
        return [EasyDict(x) for x in obj]
    elif isinstance(obj, dict):
        return EasyDict(obj)
    raise VeryHardError()


class Client:
    token = None
    room_id = None

    def __init__(self, token):
        self.token = token

    def __headers(self):
        return {'X-ChatWorkToken': self.token}

    def me(self):
        """
        Get a self introduction.

        >>> cli = Client(token)
        >>> res = cli.me()
        >>> res is not None
        True
        """
        return self.__get(_url_me)

    def my_status(self):
        """
        Get a my status.

        >>> cli = Client(token)
        >>> res = cli.my_status()
        >>> res is not None
        True
        """
        return self.__get(_url_my_status)

    def my_tasks(self, **payload):
        """
        Get a my tasks.

        >>> cli = Client(token)
        >>> res = cli.my_tasks()
        >>> res is not None
        True
        """
        return self.__get(_url_my_tasks, payload=payload)

    def visit(self, room_id):
        """
        Visit the room.

        >>> cli = Client(token)
        >>> res = cli.visit(room)
        >>> res is not None
        True
        """
        self.room_id = room_id
        return self

    def members(self):
        """
        Get members.

        >>> cli = Client(token)
        >>> res = cli.visit(room).members()
        >>> res is not None
        True
        """
        if self.room_id is None:
            raise VagabondError()
        url = _url_rooms_members.format(room_id=self.room_id)
        return self.__get(url)

    def messages(self):
        """
        Get latest messages.

        >>> cli = Client(token)
        >>> res = cli.visit(room).messages()
        >>> res is not None
        True
        """
        if self.room_id is None:
            raise VagabondError()
        url = _url_rooms_messages.format(room_id=self.room_id)
        res = self.__get(url)
        return [] if res is None else res

    def post(self, body):
        """
        Post a message in this room.

        >>> cli = Client(token)
        >>> res = cli.visit(room).post('test')
        >>> res is not None
        True
        """
        url = _url_rooms_messages.format(room_id=self.room_id)
        return self.__post(url, payload={'body': body})

    def post_to(self, to, body):
        """
        Post a message to members in this room.

        >>> cli = Client(token)
        >>> res = cli.visit(room).post_to([member1, member2], 'test')
        >>> res is not None
        True
        """
        if self.room_id is None:
            raise VagabondError()

        room_members = self.members()

        if not isinstance(to, (list, tuple)):
            to = [int(to)]

        dear = []

        for account_id in to:
            for m in room_members:
                if account_id == m['account_id']:
                    dear.append(
                        u('[To:{0}] {1}さん').format(
                            m['account_id'], m['name']))
                    break

        body = '\n'.join(dear) + '\n' + u(body)

        return self.post(body)

    def post_to_all(self, body):
        """
        Post a message to all members in this room.

        >>> cli = Client(token)
        >>> res = cli.visit(room).post_to_all('test to all')
        >>> res is not None
        True
        """
        if self.room_id is None:
            raise VagabondError()
        room_members = self.members()
        to = u('[To:{0}] {1}さん')
        to_all = [to.format(m['account_id'], m['name']) for m in room_members]
        body = '\n'.join(to_all) + '\n' + u(body)
        return self.post(body)

    def __get(self, url, **kwargs):
        params = kwargs['payload'] if 'payload' in kwargs else None
        response = requests.get(url, params=params, headers=self.__headers())
        return self.__process_response(response)

    def __post(self, url, **kwargs):
        data = kwargs['payload'] if 'payload' in kwargs else None
        response = requests.post(url, data=data, headers=self.__headers())
        return self.__process_response(response)

    def __process_response(self, response):
        logging.debug('url: {0}'.format(response.url))
        logging.debug('status_code: {0}'.format(response.status_code))
        logging.debug('encoding: {0}'.format(response.encoding))
        logging.debug('header: {0}'.format(response.headers))
        logging.debug('text: {0}'.format(response.text))
        if response.status_code == 200:
            json = response.json()
            return _to_easy(json)
        return None


def auth(token):
    return Client(token)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
