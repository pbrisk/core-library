import socket
import sys

from businessdate import BusinessDate, BusinessPeriod
from unicum import Session, Server

sys.path.append('.')

SERVER_NAME = 'corelibrary-server'


class CoreSession(Session):
    """ api session to handle request in multiprocessing """
    import corelibrary

    _module = corelibrary
    _class = _module.VisibleObject
    _default_key_start = 'arg'
    _types = {
        'cls': (lambda c: getattr(_module, c)),
        'self': (lambda s: _class if s in _class.keys() else 'Object %s does not exit yet. Use create().' %_class.__name__),
        'date': BusinessDate,
        'period': BusinessPeriod,
        'number': int,
        'year': int,
        'month': int,
        'day': int,
        'int': int,
        'long': long,
        'float': float,
        'value': float,
        'str': str,
        'name': str,
        'bool': (lambda x: bool(0) if x=='False' else bool(x)),
        'flag': (lambda x: bool(0) if x=='False' else bool(x)),
        'variant': (lambda x: x)
    }


class CoreApp(Server):
    """ corelibrary rest api web service """

    def __init__(self, session=CoreSession, import_name=SERVER_NAME, host=None, port=2699):
        super(CoreApp, self).__init__(session=session, import_name=import_name)
        if host is None:
            host = socket.gethostbyname(socket.gethostname())
        self._host = host
        self._port = port

    def run(self):
        """ run app """
        super(CoreApp, self).run(host=self._host, port=self._port)


if __name__ == '__main__':
    # uncomment this to run server using own ip
    # Server().run(socket.gethostbyname(socket.gethostname()), 2699)
    Server(CoreSession, import_name=SERVER_NAME).run('127.0.0.1', 2699)
