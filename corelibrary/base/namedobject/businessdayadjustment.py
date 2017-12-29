# coding=utf-8
""" factory for BusinessDayAdjustment """
from businessdate import BusinessDate, DEFAULT_HOLIDAYS
from unicum import FactoryObject


class BusinessDayAdjustment(FactoryObject):
    """ abstract basis class for business day adjustment methods """
    __factory = dict()

    def __init__(self, *args):
        super(BusinessDayAdjustment, self).__init__()
        self.holidays = DEFAULT_HOLIDAYS

    def adjust(self, business_date, holiday_obj=None):
        """
        calculate adjusted business day resp given holiday object

        :param BusinessDate business_date: start date
        :param businessholidays holiday_obj: holiday calendar
        :return BusinessDate:
        """
        pass


class Follow(BusinessDayAdjustment):
    """ class implements Follow business day adjustment method """

    def adjust(self, business_date, holiday_obj=None):
        """
        calculate adjusted business day resp given holiday object

        :param BusinessDate business_date: start date
        :param holiday holiday_obj: holiday calendar
        :return BusinessDate:
        """
        if not holiday_obj:
            holiday_obj = self.holidays
        return BusinessDate.adjust_follow(business_date, holiday_obj)


class Previous(BusinessDayAdjustment):
    """ class implements Previous business day adjustment method """

    def adjust(self, business_date, holiday_obj=None):
        """
        calculate adjusted business day resp given holiday object

        :param BusinessDate business_date: start date
        :param businessholidays holiday_obj: holiday calendar
        :return BusinessDate:
        """
        if not holiday_obj:
            holiday_obj = self.holidays
        return BusinessDate.adjust_previous(business_date, holiday_obj)


class ModFollow(BusinessDayAdjustment):
    """ class implements ModFollow business day adjustment method """

    def adjust(self, business_date, holiday_obj=None):
        """
        calculate adjusted business day resp given holiday object

        :param BusinessDate business_date: start date
        :param businessholidays holiday_obj: holiday calendar
        :return BusinessDate:
        """
        if not holiday_obj:
            holiday_obj = self.holidays
        return BusinessDate.adjust_mod_follow(business_date, holiday_obj)


class ModPrevious(BusinessDayAdjustment):
    """ class implements ModPrevious business day adjustment method """

    def adjust(self, business_date, holiday_obj=None):
        """
        calculate adjusted business day resp given holiday object

        :param BusinessDate business_date: start date
        :param businessholidays holiday_obj: holiday calendar
        :return BusinessDate:
        """
        if not holiday_obj:
            holiday_obj = self.holidays
        return BusinessDate.adjust_mod_previous(business_date, holiday_obj)


# register instances

Follow().register()
Follow().register('Following')
Previous().register()
ModFollow().register()
ModFollow().register('ModFollowing', 'ModifiedFollowing')
ModPrevious().register()
ModPrevious().register('ModPrevious', 'ModifiedPrevious')
