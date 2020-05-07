from datetime import datetime
from mosenergosbyt.measure import Measure
import calendar
import logging

_LOGGER = logging.getLogger(__name__)


class MeterException(BaseException):
    pass


class Meter:
    def __init__(self,**kwargs):
        self.session = kwargs['session']
        self.nn_ls = kwargs['nn_ls']
        self.__vl_provider = kwargs['vl_provider']
        self.id_service = kwargs.get('id_service',None)
        self.nm_ls_group_full = kwargs.get('nm_ls_group_full',None)
        self.nm_provider = kwargs.get('nm_provider', None)
        self.nn_days = None
        self.vl_debt = None
        self.vl_balance = None
        self.measure_list = []

    @property
    def vl_provider(self):
        if not self.__vl_provider:
            raise MeterException(
                'для получения списка переданных показаний нужно получить информацию о плательщике'
            )
        return self.__vl_provider

    @classmethod
    def parse(cls,**kwargs):
        return cls(**kwargs)

    def get_measure_list(self) -> list:
        """
        Получение списка переданных ранее показаний
        :return:
        """
        data = self.__get_measure_imp(proxyquery='Indications')
        self.measure_list = [Measure.parse(**item) for item in data]
        return self.measure_list

    def get_balance(self):
        data = self.__get_measure_imp(proxyquery='CurrentBalance')
        self.vl_balance = data[0].get('vl_balance',None)
        self.vl_debt = data[0].get('vl_debt', None)
        return self.measure_list

    def get_indication(self):
        data = self.__get_measure_imp(proxyquery='IndicationCounter')
        self.nn_days = data[0].get('nn_days',None)
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
                obj = mld.get(Measure.parse_date(item['dt_pay']), None)
                if not obj:
                    _LOGGER.warning('получена информация об оплате показаний, которых нет в списке')
                    continue
                obj.update(**item)
        else:
            self.measure_list = [Measure.parse(**item) for item in data]

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

    @property
    def last_measure(self):
        if not self.measure_list:
            raise MeterException(
                'Отсутствует список переданных показаний'
            )

        return max(self.measure_list, key=lambda x: x.dt_indication)

    def upload_measure(self, measure_day: int, measure_night=None, measure_middle=None) -> None:
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
        year = datetime.now().year
        month = datetime.now().month
        date = self.last_measure.dt_indication
        if date.year == year and date.month == month:
            raise MeterException(
                'Показания уже были преданы в этом месяце (%s)' % date
            )

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
            text = 'Ошибка портала'
            if len(resp) and 'nm_result' in resp[0] and resp[0]['nm_result']:
                text = resp[0]['nm_result']
            raise MeterException(text)

        return resp[0]['nm_result']