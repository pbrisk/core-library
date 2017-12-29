# coding=utf-8
"""
module containing compounding classes
"""
from dcf import simple_compounding, simple_rate, continuous_compounding, continuous_rate, \
    periodic_compounding, periodic_rate
from unicum import FactoryObject


class Compounding(FactoryObject):
    """ abstract basis class for compounding methods """
    __factory = dict()

    def __init__(self, *args):
        super(Compounding, self).__init__()

    @staticmethod
    def rate_from_disc_factor(start, end, dcc, df):
        """
        calculates rate between given dates (start date excluded, end date included) from given discount factor

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double df : discount factor
        :return double : rate
        """
        pass

    @staticmethod
    def disc_factor_from_rate(start, end, dcc, rate):
        """
        calculates discount factor between given dates (start date excluded, end date included) from given rate

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double rate : discount rate
        :return double : discount factor
        """
        pass


class Continuous(Compounding):
    """ continuous compounding method """

    @staticmethod
    def disc_factor_from_rate(start, end, dcc, rate):
        """
        calculates discount factor between given dates (start date excluded, end date included) from given rate

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double rate : discount rate
        :return double : discount factor
        """
        return continuous_compounding(rate, dcc.get_year_fraction(start, end))

    @staticmethod
    def rate_from_disc_factor(start, end, dcc, df):
        """
        calculates rate between given dates (start date excluded, end date included) from given discount factor

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double df : discount factor
        :return double : rate
        """
        return continuous_rate(df, dcc.get_year_fraction(start, end))


class Simple(Compounding):
    """ simple compounding method """

    @staticmethod
    def disc_factor_from_rate(start, end, dcc, rate):
        """
        calculates discount factor between given dates (start date excluded, end date included) from given rate

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double rate : discount rate
        :return double : discount factor
        """

        return simple_compounding(rate, dcc.get_year_fraction(start, end))

    @staticmethod
    def rate_from_disc_factor(start, end, dcc, df):
        """
        calculates rate between given dates (start date excluded, end date included) from given discount factor

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double df : discount factor
        :return double : rate
        """

        return simple_rate(df, dcc.get_year_fraction(start, end))


class Discrete(Compounding):
    """
    general discrete compounding method
    """

    def __init__(self, freq=1):
        super(Discrete, self).__init__()
        self.disc_factor_from_rate = \
            lambda start, end, dcc, rate: periodic_compounding(rate, dcc.get_year_fraction(start, end), freq)
        self.rate_from_disc_factor = \
            lambda start, end, dcc, df: periodic_rate(df, dcc.get_year_fraction(start, end), freq)


class Annually(Compounding):
    """ annually compounding method """

    @staticmethod
    def disc_factor_from_rate(start, end, dcc, rate):
        """
        calculates discount factor between given dates (start date excluded, end date included) from given rate

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double rate : discount rate
        :return double : discount factor
        """

        return periodic_compounding(rate, dcc.get_year_fraction(start, end), 1)

    @staticmethod
    def rate_from_disc_factor(start, end, dcc, df):
        """
        calculates rate between given dates (start date excluded, end date included) from given discount factor

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double df : discount factor
        :return double : rate
        """

        return periodic_rate(df, dcc.get_year_fraction(start, end), 1)


class SemiAnnually(Compounding):
    """ semiannually compounding method """

    @staticmethod
    def disc_factor_from_rate(start, end, dcc, rate):
        """
        calculates discount factor between given dates (start date excluded, end date included) from given rate

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double rate : discount rate
        :return double : discount factor
        """

        return periodic_compounding(rate, dcc.get_year_fraction(start, end), 2)

    @staticmethod
    def rate_from_disc_factor(start, end, dcc, df):
        """
        calculates rate between given dates (start date excluded, end date included) from given discount factor

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double df : discount factor
        :return double : rate
        """

        return periodic_rate(df, dcc.get_year_fraction(start, end), 2)


class Quarterly(Compounding):
    """ quarterly compounding method """

    @staticmethod
    def disc_factor_from_rate(start, end, dcc, rate):
        """
        calculates discount factor between given dates (start date excluded, end date included) from given rate

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double rate : discount rate
        :return double : discount factor
        """

        return periodic_compounding(rate, dcc.get_year_fraction(start, end), 4)

    @staticmethod
    def rate_from_disc_factor(start, end, dcc, df):
        """
        calculates rate between given dates (start date excluded, end date included) from given discount factor

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double df : discount factor
        :return double : rate
        """

        return periodic_rate(df, dcc.get_year_fraction(start, end), 4)


class Monthly(Compounding):
    """ monthly compounding method """

    @staticmethod
    def disc_factor_from_rate(start, end, dcc, rate):
        """
        calculates discount factor between given dates (start date excluded, end date included) from given rate

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double rate : discount rate
        :return double : discount factor
        """

        return periodic_compounding(rate, dcc.get_year_fraction(start, end), 12)

    @staticmethod
    def rate_from_disc_factor(start, end, dcc, df):
        """
        calculates rate between given dates (start date excluded, end date included) from given discount factor

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double df : discount factor
        :return double : rate
        """

        return periodic_rate(df, dcc.get_year_fraction(start, end), 12)


class Daily(Compounding):
    """ daily compounding method """

    @staticmethod
    def disc_factor_from_rate(start, end, dcc, rate):
        """
        calculates discount factor between given dates (start date excluded, end date included) from given rate

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double rate : discount rate
        :return double : discount factor
        """

        return periodic_compounding(rate, dcc.get_year_fraction(start, end), 365)

    @staticmethod
    def rate_from_disc_factor(start, end, dcc, df):
        """
        calculates rate between given dates (start date excluded, end date included) from given discount factor

        :param BusinessDate start : start date of BusinessPeriod
        :param BusinessDate end : end date of BusinessPeriod
        :param dcc dcc : BusinessPeriod day count convention
        :param double df : discount factor
        :return double : rate
        """

        return periodic_rate(df, dcc.get_year_fraction(start, end), 365)


# register instances

Continuous().register()
Simple().register()
Daily().register()
Monthly().register()
Quarterly().register()
SemiAnnually().register()
Annually().register()
