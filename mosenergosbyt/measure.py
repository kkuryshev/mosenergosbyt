from datetime import datetime

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

    def update(self, **kwargs):
        [self.__setattr__(item[0], item[1]) for item in kwargs.items() if item[0] in self.__dict__.keys()]
        return self

    @property
    def pay_date(self):
        return datetime.strptime(self.dt_pay,DATE_PATTERN)

    @property
    def indication_date(self):
        return datetime.strptime(self.dt_indication,DATE_PATTERN)