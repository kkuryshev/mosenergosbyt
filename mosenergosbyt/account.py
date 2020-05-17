from mosenergosbyt.meter import Meter
import logging

_LOGGER = logging.getLogger(__name__)


class AccountException(BaseException):
    pass


class Account:
    def __init__(self, session):
        self.session = session
        self.__meter_list = []

    def get_info(self,with_measure=False,indications=False,balance=False) -> None:
        """
        Получение базовой информации клиента с портала, которая нужна для последующих вызовов
        :return:
        """
        self.__meter_list = []
        data = self.session.call('LSList')
        for item in data:
            obj = Meter.parse(session=self.session, **item)
            if with_measure:
                obj.get_measure_list()
                obj.get_payment_list()
            if indications:
                obj.get_indication()
            if balance:
                obj.get_balance()

            self.__meter_list.append(obj)

    @property
    def meter_list(self):
        if not self.__meter_list:
            raise AccountException(
                'Отсутствует информация о счетчиках'
            )
        return {item.nn_ls: item for item in self.__meter_list}
