# coding=utf-8
"""
module containing frequency classes
"""
from businessdate import BusinessPeriod
from unicum import FactoryObject


class Frequency(FactoryObject):
    """ abstract basis class for time BusinessPeriod frequencies """
    __factory = dict()

    def __init__(self, *args):  # pylint : disable=unused-argument
        super(Frequency, self).__init__()

    @property
    def year_fraction(self):
        """
        gives wave length of frequency in term of year fraction

        :return double :
        """
        return 0.0

    @property
    def period(self):
        """
        gives frequency in term of BusinessPeriod

        :return BusinessPeriod :
        """
        return BusinessPeriod()


class Annually(Frequency):
    """ class implements annually frequency """
    _year_faction = 1.0
    _period = BusinessPeriod(years=1)

    @property
    def year_fraction(self):
        """
        gives wave length of frequency in term of year fraction

        @return double :
        """
        return Annually._year_faction

    @property
    def period(self):
        """
        gives frequency in term of BusinessPeriod

        :return BusinessPeriod :
        """
        return Annually._period


class SemiAnnually(Frequency):
    """ class implements annually frequency """
    _year_faction = 0.5
    _period = BusinessPeriod(months=6)

    @property
    def year_fraction(self):
        """
        gives wave length of frequency in term of year fraction

        @return double :
        """
        return SemiAnnually._year_faction

    @property
    def period(self):
        """
        gives frequency in term of BusinessPeriod

        :return BusinessPeriod :
        """
        return SemiAnnually._period


class Quarterly(Frequency):
    """ class implements quarterly frequency """
    _year_faction = 0.25
    _period = BusinessPeriod(months=3)

    @property
    def year_fraction(self):
        """
        gives wave length of frequency in term of year fraction

        @return double :
        """
        return Quarterly._year_faction

    @property
    def period(self):
        """
        gives frequency in term of BusinessPeriod

        :return BusinessPeriod :
        """
        return Quarterly._period


class Monthly(Frequency):
    """ class implements monthly frequency """
    _year_faction = 1 / 12
    _period = BusinessPeriod(months=1)

    @property
    def year_fraction(self):
        """
        gives wave length of frequency in term of year fraction

        @return double :
        """
        return Monthly._year_faction

    @property
    def period(self):
        """
        gives frequency in term of BusinessPeriod

        :return BusinessPeriod :
        """
        return Monthly._period


Annually().register()
Annually().register("annually", "ANNUALLY", "1Y", "1y", "1 Years", "12M", "12m", "12 Months")

SemiAnnually().register()
SemiAnnually().register("Semi", "semiannually", "semi", "SEMIANNUALLY", "SEMI", "6M", "6m", "6 Months")

Quarterly().register()
Quarterly().register("quarterly", "QUARTERLY", "3M", "3m", "3 Months", "1Q", "1q", "1 Quaters")

Monthly().register()
Monthly().register("Monthly", "monthly", "MONTHLY", "1M", "1m", "1 Months")
