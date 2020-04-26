from mosenergosbyt.measure import Measure
from datetime import datetime
import calendar
import logging

_LOGGER = logging.getLogger(__name__)


class AccountException(BaseException):
    pass


class Account:
    def __init__(self, session, payload):
        """
        :param session: сессия портала
        :type: mosenergosbyt.Session
        :param payload: номер ЛК
        :type payload: str
        """
        self.session = session
        self.payload = payload
        self.id_service = None
        self.nm_ls_group_full = None
        self.__vl_provider = None
        self.measure_list = []

    @property
    def vl_provider(self):
        if not self.__vl_provider:
            raise AccountException(
                'для получения списка переданных показаний нужно получить информацию о плательщике'
            )
        return self.__vl_provider

    def get_info(self) -> None:
        """
        Получение базовой информации клиента с портала, которая нужна для последующих вызовов
        :return:
        """
        data = self.session.call('LSList')
        try:
            lk = next((item for item in data if item['nn_ls'] == self.payload))
        except StopIteration:
            raise AccountException(
                'не найдена информация о ЛК %s' % self.payload
            )

        self.nm_ls_group_full = lk['nm_ls_group_full']
        self.id_service = lk['id_service']
        self.__vl_provider = lk['vl_provider']

    def get_measure_list(self) -> list:
        """
        Получение списка переданных ранее показаний
        :return:
        """
        data = self.__get_measure_imp(proxyquery='Indications')
        self.measure_list = [Measure(**item) for item in data]
        return self.measure_list

    def get_payment_list(self) -> list:
        """
        Получение списка оплат
        :return:
        """
        data = self.__get_measure_imp(proxyquery='Pays')
        if self.measure_list:
            mld = {item.dt_indication: item for item in self.measure_list}
            for item in data:
                obj = mld.get(item['dt_pay'], None)
                if not obj:
                    _LOGGER.warning('получена информация об оплате показаний, которых нет в списке')
                    continue
                obj.set_payment(**item)
        else:
            self.measure_list = [Measure(**item) for item in data]

        return self.measure_list

    def __get_measure_imp(self, proxyquery) -> dict:
        """
        Запрос к порталу для получения списка оплат/переданных показаний
        :param proxyquery: тип запроса
        :return:
        """
        year = datetime.now().year
        month = datetime.now().month
        last_date = calendar.monthrange(year, month)[1]

        return self.session.call('bytProxy', data={
            'dt_en': datetime(year, month, last_date, 23, 59, 59).astimezone().isoformat(),
            'dt_st': datetime(year, month - 2, 1).astimezone().isoformat(),
            'plugin': 'bytProxy',
            'proxyquery': proxyquery,
            'vl_provider': self.vl_provider
        })

    def upload_measure(self, measure_day, measure_night=None, measure_middle=None) -> None:
        """
        Передача показаний
        :param measure_day: дневные показания
        :type measure_day: int
        :param measure_night: ночные показания (если счетчик 2/3-ех тарифный)
        :type measure_night: int
        :param measure_middle: вечерние показания (если счетчик 3-ех тарифный)
        :type measure_middle: int
        :return:
        """
        vl_list = {
            'plugin': 'bytProxy',
            'pr_flat_meter': '0',
            'proxyquery': 'CalcCharge',
            'vl_provider': self.vl_provider,
            'vl_t1': measure_day
        }
        if measure_night:
            vl_list.update({'vl_t2': measure_night})
        if measure_middle:
            vl_list.update({'vl_t3': measure_middle})

        resp = self.session.call(
            'bytProxy',
            data=vl_list
        )

        if not resp[0]['pr_correct']:
            raise AccountException(resp[0]['nm_result'])

