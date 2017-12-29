# coding=utf-8

from businessdate import BusinessPeriod

from corelibrary.base.baseobject import AnalyticsObject


class DefaultProbabilityInterface(AnalyticsObject):
    """ interface class for default probability """

    def _day_count(self, start_date, end_date):
        """
        calculates day count

        :param BusinessDate end_date:
        :param BusinessDate start_date:
        :return float:
        """
        raise NotImplementedError

    def get_survival_probability(self, pd_value, end_date, start_date=None):
        """ returns the annualized and cumulative survival probability for a given rating resp. pd and date

        Parameters:
            pd_value (float): the current pd
            start_date (BusinessDate): date of pd observation
            end_date (BusinessDate): if given, average pd between start date (included) and end date
                                     (excluded) is given
        Returns:
            float: survival probability

        The method has to be implemented in the sub classes
        of :py:class:`defaultcurve.defaultcurve.DefaultProbability`.

        Derives the probability (depending on a rating or spot (annual) default probability) to survive,
        e.g. not to migrate to rating 'D', in a given BusinessPeriod of time. This time BusinessPeriod is given by
        base_date (start date of BusinessPeriod) and value_date (end date of BusinessPeriod)
        """
        raise NotImplementedError

    def get_default_probability(self, pd_value, end_date, start_date=None):
        """ Returns the annualized and cumulative default probability for a given rating resp. pd and date

        Parameters:
            pd_value (float): the current pd
            start_date (BusinessDate): date of pd observation
            end_date (BusinessDate): if given, average pd between start date (included) and end date
                                     (excluded) is given
        Returns:
            float: default probability

        Derives the probability (depending on a rating or spot (annual) default probability) to default,
        e.g. to migrate to rating 'D', in a given BusinessPeriod of time. This time BusinessPeriod is given by
        base_date (start date of BusinessPeriod) and value_date (end date of BusinessPeriod)
        """

        return 1 - self.get_survival_probability(pd_value, end_date, start_date)

    def get_forward_default_probability(self, pd_value, start_date, end_date=None, tenor_period=BusinessPeriod('1y')):
        """ return annualized forward default probability

        Parameters:
            pd_value (float): pd for the calculation
            start_date (BusinessDate): start date of conditional deflaut period
            end_date (BusinessDate): end date of conditional deflaut period
            tenor_period (BusinessPeriod): period length of conditional deflaut period

        Returns:
            float: forward default probability
        """
        end_date = start_date + tenor_period if end_date is None else end_date
        sv = self.get_survival_probability(pd_value, end_date, start_date)
        t = self._day_count(start_date, end_date)
        return (1.0 - sv) / t
