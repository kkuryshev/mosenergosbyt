class Measure:
    def __init__(self, **kwargs):
        self.dt_indication = None
        self.status = None
        self.sum = None

        [self.__setattr__(item[0], item[1]) for item in kwargs.items()]

    def set_payment(self, **kwargs):
        self.status = kwargs.get('nm_status',None)
        self.sum = kwargs.get('sm_pay',None)
