from datetime import datetime
import re

DATE_PATTERN = '%Y-%m-%d %H:%M:%S'


class Measure:
    def __init__(self):
        self.dt_pay = None  # дата оплаты
        self.nm_status = None  # статус зачисления
        self.sm_pay = None  # оплаченная сумма
        self.dt_meter_installation = None  # дата постановки счетчика на учтет
        self.dt_indication = None  # дата передачи показаний
        self.nm_description_take = None  # описниае
        self.nm_take = None  # кем переданы показания
        self.nm_t1 = None  # зоны тарифа
        self.nm_t2 = None
        self.nm_t3 = None
        self.pr_zone_t1 = None  # часы тарифов
        self.pr_zone_t2 = None
        self.pr_zone_t3 = None
        self.vl_t1 = None  # показания для тарифа
        self.vl_t2 = None
        self.vl_t3 = None

    @classmethod
    def parse(cls, **kwargs):
        for item in kwargs.items():
            if not isinstance(item[1], str):
                continue
            if re.search(r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', item[1]):
                kwargs.update(
                    {
                        item[0]:
                            cls.parse_date(item[1])
                    }
                )
        obj = cls()
        return obj.update(**kwargs)

    @staticmethod
    def parse_date(str_dt):
        return datetime.strptime(str_dt, DATE_PATTERN)

    def update(self, **kwargs):
        [self.__setattr__(item[0], item[1]) for item in kwargs.items() if item[0] in self.__dict__.keys()]
        return self
