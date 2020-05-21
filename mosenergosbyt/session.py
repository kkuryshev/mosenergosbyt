import logging
from requests import session
from requests.exceptions import Timeout, RequestException
from mosenergosbyt.exceptions import *
import json

_LOGGER = logging.getLogger(__name__)

if _LOGGER.getEffectiveLevel() == 10:  # DEBUG
    import http
    http_client = logging.getLogger('urllib3.connectionpool')
    http_client.setLevel(logging.INFO)
    http.client.HTTPConnection.debuglevel = 1


def check_response(resp):
    if resp.status_code != 200:
        raise SessionException(
            'получен не корректный ответ от портала %s' % resp.status_code
        )

    j = resp.json()
    _LOGGER.debug(j)
    if not j['success']:
        if j['err_code'] == 201:
            raise InvalidSession(
                j['err_text']
            )
        raise SessionException(
            'ошибка авторизации'
        )

    if 'data' not in j:
        raise SessionException(
            'не корректный ответ'
        )

    return j['data']


def check_auth_response(resp):
    if not resp:
        raise SessionException(
            'не корректный ответ'
        )

    data = resp[0]
    if data['kd_result']:
        raise SessionException(
            'ошибка авторизации: %s' % data['nm_result']
        )

    return data


class Session:
    __session = None

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.token = None
        self.id_profile = None

    def __establish(self) -> None:
        self.__session = session()

        resp = self.call(
            query='login', action='auth',
            data={
                'login': self.login,
                'psw': self.password,
                'vl_device_info': json.dumps(
                    {"appver": "1.15.0", "type": "browser",
                     "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) " +
                                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
                     }
                )
            }
        )

        data = check_auth_response(resp)

        self.token = data['session']
        self.id_profile = data['id_profile']

        self.call('Init')

    def call(self, query, action='sql', data=None, **kwargs) -> dict:
        """
        адаптер вызова портала
        :param query: наименование операции
        :type query: str
        :param action: тип операции (по умлочанию sql)
        :type action: str
        :param data: дополнительные данные для передачи в теле post
        :type data: dict
        :return:
        """
        _LOGGER.debug(f'query={query},action={action},data={data}')
        if not self.__session:
            self.__establish()

        try:
            resp = self.__session.post(
                'https://my.mosenergosbyt.ru/gate_lkcomu',
                headers={
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin'
                },
                params={
                    'action': action,
                    'query': query,
                    'session': self.token
                },
                data=data,
                timeout=kwargs.get('timeout', None)
            )
        except RequestException as e:
            if isinstance(e, Timeout):
                raise SessionTimeout(e)
            else:
                raise SessionException(e)

        try:
            return check_response(resp)
        except InvalidSession as e:
            if kwargs.get('retry', False):
                raise e

            logging.info(f'сессия не валидна, нужно сделать переподключение ({e})')
            self.__session = None
            return self.call(query=query, action=action, data=data, retry=True)
