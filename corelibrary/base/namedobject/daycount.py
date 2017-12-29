# coding=utf-8
"""
module containing daycount classes
"""
from businessdate import BusinessDate
from unicum import FactoryObject


class DayCount(FactoryObject):
    """ abstract basis class for day count methods """
    __factory = dict()

    def __init__(self, *args):  # pylint : disable=unused-argument
        super(DayCount, self).__init__()

    def get_year_fraction(self, start, end):
        """
        calculate year fraction between given dates (start date excluded, end date included)

        :param BusinessDate start: start date of BusinessPeriod
        :param BusinessDate end: end date of BusinessPeriod
        :return float:
        """

        return start.diff_in_years(end)

    def __call__(self, start, end):
        return self.get_year_fraction(start, end)


class D30360(DayCount):
    """ class implements 30/360 day count convention """

    def get_year_fraction(self, start, end):
        """
        calculate year fraction between given dates (start date excluded, end date included)

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :return float:
        """
        return BusinessDate.get_30_360(start, end)


class Act36525(DayCount):
    """ class implements act/365 day count convention """

    def get_year_fraction(self, start, end):
        """
        calculate year fraction between given dates (start date excluded, end date included)

        :param BusinessDate start: start date of BusinessPeriod
        :param BusinessDate end: end date of BusinessPeriod
        :return float:
        """
        return BusinessDate.get_act_36525(start, end)


class Act365(DayCount):
    """ class implements act/365 day count convention """

    def get_year_fraction(self, start, end):
        """
        calculate year fraction between given dates (start date excluded, end date included)

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :return float:
        """
        return BusinessDate.get_act_365(start, end)


class Act360(DayCount):
    """ class implements act/360 day count convention """

    def get_year_fraction(self, start, end):
        """
        calculate year fraction between given dates (start date excluded, end date included)

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :return float:
        """

        return BusinessDate.get_act_360(start, end)


class ActAct(DayCount):
    """ class implements act/act day count convention """

    def get_year_fraction(self, start, end):
        """
        calculate year fraction between given dates (start date excluded, end date included)

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :return float:
        """

        return BusinessDate.get_act_act(start, end)


# register instances

D30360().register()
D30360().register("30/360", "360/360", "Bond Basis")

Act36525().register()
Act36525().register("act/365.25", "act365.25", "Act/365.25", "ACT365.25", "ACT365.25")

Act365().register()
Act365().register("act365", "act/365", "Act/365", "ACT/365", "ACT365")

Act360().register()
Act360().register("act360", "ACT360", "act/360", "Act/360", "ACT/360")

ActAct().register()
ActAct().register("act/act", "Act/Act", "ACT/ACT", "actact", "ActualActual", "actual")
