# coding=utf-8
""" calendars as named objects """
import calendar
from businessdate import BusinessDate
from unicum import FactoryObject
from datetime import date
from dateutil.easter import easter
from dateutil.relativedelta import relativedelta as rd


class Calendar(FactoryObject):
    """ Calendar base class """

    __factory = dict()

    def __init__(self, holiday_list = list()):
        """
        :param iterable holiday_list:   This should be a container object of holidays
                                        which is accessible with "in" (eg. date in holiday_obj)
        """
        super(Calendar, self).__init__()
        if isinstance(holiday_list, (list, tuple)):
            holiday_list = [BusinessDate(x).to_date() for x in holiday_list]

        if isinstance(holiday_list, str):
            self._inner_cal= self._union_of_registered_calendars(holiday_list)
        else:
            self._inner_cal = holiday_list

    def __contains__(self, key):
        if isinstance(key, BusinessDate):
            key = key.to_date()
        return key in self._inner_cal

    def is_holiday(self, business_date):
        """ is_holiday method """
        return business_date in self

    def is_business_day(self, business_date):
        """ is_business_day method """
        return BusinessDate.is_businessday(business_date, self)

    @staticmethod
    def is_weekend(business_date):
        """ is_weekend method """
        return calendar.weekday(business_date.year, business_date.month, business_date.day) > calendar.FRIDAY

    def _union_of_registered_calendars(self, string):
        calnames = string.replace(' ', '').split(',')

        class CalendarUnion(object):
            def __init__(self, inner_calendar_list):
                self._calendars = inner_calendar_list

            def __contains__(self, key):
                for cal in self._calendars:
                    if key in cal:
                        return True
                return False

        inner_cals = [Calendar(name)._inner_cal for name in calnames if name in Calendar._get_factory()]

        return CalendarUnion(inner_cals)

    def __reduce__(self):
        l = [k for k,v in self.__class__.items() if v == self]
        cal_str = l[0]
        return Calendar, (cal_str,)


class target2_calendar(object):
    """ target 2 calendar """
    def __contains__(self, key):

        e = easter(key.year)
        return key in [date(key.year, 1, 1), e - rd(days=2), e + rd(days=1), date(key.year, 5, 1), date(key.year, 12, 25), date(key.year, 12, 26)]


class TAR(Calendar):
    """ TARGET2 calendar """
    def __init__(self):
        super(TAR, self).__init__(target2_calendar())

TAR().register()
