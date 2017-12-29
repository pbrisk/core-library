# coding=utf-8

import businessdate
import dcf

from corelibrary.base.baseobject import DataRange
from corelibrary.base.interface.defaultcurve import DefaultProbabilityInterface
from corelibrary.base.interface.masterscale import MasterScaleInterface
from corelibrary.base.namedobject import Annually, IntensityCalculation, ActAct
from corelibrary.utils.maths import matrix, expm, logm, epsilon, exp, log


class DefaultProbability(DefaultProbabilityInterface):
    r""" root class for default probability classes

    Default probabilities derive the the probability of an entity depending on a rating to default, e.g.
    to migrate to rating 'D', in a given BusinessPeriod of time. Basic model is a state space :math:`S` spanned
    by finite many rating classes :math:`R_i, i = 1 \dots n`. The classes are given by a master scale and represent
    the *pure states* :math:`b_i`, which form a real numbered valued basis of :math:`S`.

    Hence :math:`S` is understood as the positive cone of real vector space

    .. math::
        :nowrap:

        \[
            S = \{ (x_i) \in \mathbb{R} \| x_i \geq 0 \text{ for }
                \sum_{i =1 \dots n} x_i b_i = x \}
        \]

    Elements of :math:`S` which are not represented by canonical basis elements :math:`e_i` are referred
    as *mixed states*.
    """

    @property
    def master_scale(self):
        """ master scale """
        return self._master_scale_

    def __init__(self, object_name_str=''):
        """

        :param object_name_str:
        """
        super(DefaultProbability, self).__init__(object_name_str)
        self._master_scale_ = MasterScaleInterface()
        self._day_count_ = ActAct()

    def _rebuild_object(self):
        pass

    def _day_count(self, start_date, end_date):
        return self._day_count_

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

        assert isinstance(pd_value, float), 'a probability should be float not %s' % str(type(pd_value))
        assert 0.0 <= pd_value <= 1.0, 'a probability should be between 0.0 and 1.0 not %f' % pd_value

        if not start_date:
            start_date = self.origin
        s = start_date.to_businessdate(self.origin)
        e = end_date.to_businessdate(self.origin)
        t = businessdate.BusinessDate.diff_in_years(s, e)

        # calc (constant) hazard rate
        if 1.0 - pd_value < epsilon:
            return 1.0
        h = -1.0 * log(1.0 - pd_value)

        return exp(-1.0 * h * t)


class ProbabilityList(DefaultProbability):
    """ ProbabilityList holds default probabilities as curves per rating """

    @classmethod
    def from_default_probability(cls, default_probability_obj, date_list=None):
        """
        build ProbabilityList from other DefaultProbability

        :param default_probability_obj: other DefaultProbability
        :param date_list: dates to genereate list
        :return: ProbabilityList object
        """
        if not date_list:
            date_list = businessdate.BusinessPeriod('1Y') * range(1, 101, 1)
        prob_list = [[' ']]
        prob_list[0].extend(default_probability_obj.master_scale.rating_list)

        for d in date_list:
            prob_line = list()
            prob_line.append(d)
            for r in default_probability_obj.master_scale.rating_list:
                prob_line.append(default_probability_obj.get_default_probability(r, d))
            prob_list.append(prob_line)

        prob_datarange = DataRange(prob_list)

        obj = ProbabilityList(default_probability_obj.object_name + '_ProbabilityList')
        obj.modify_object('ObjectOrigin', default_probability_obj.origin)
        obj.modify_object('MasterScaleInterface', default_probability_obj.master_scale)
        obj.modify_object('ProbabilityList', prob_datarange)
        obj.modify_object('ProbabilityType', IntensityCalculation('CumulativePD'))

        return obj

    def __init__(self, object_name_str=''):
        super(ProbabilityList, self).__init__(object_name_str)

        self._probability_type_ = IntensityCalculation('CumulativePD')
        self._probability_list_ = DataRange([[' ', 'A', 'B', 'C', 'D'],
                                             ['0D', 0.001, 0.010, 0.100, 1.000],
                                             ['1Y', 0.001, 0.010, 0.100, 1.000]])
        self._pd_curve_dict = dict()
        self._rebuild_object()

    def _rebuild_object(self):
        date_list = [businessdate.BusinessPeriod(p) for p in self._probability_list_.row_keys()]
        date_list = [p.to_businessdate(self.origin) for p in date_list]
        year_fraction_list = [businessdate.BusinessDate.diff_in_years(self.origin, d) for d in date_list]

        for r in self._probability_list_.col_keys():
            zeros_list = self._probability_type_.convert_list(year_fraction_list, self._probability_list_.get_column(r))
            self._pd_curve_dict[r] = dcf.ZeroRateCurve(date_list,
                                                       zeros_list,
                                                       (dcf.left(), dcf.left(), dcf.left()),
                                                       self.origin)

        return self

    def get_survival_probability(self, pd_value, end_date, start_date=None):
        """

        :param pd_value:
        :param end_date:
        :param start_date:
        :return:
        """
        weights = self._master_scale_.get_rating_weights_from_default_probability(pd_value)
        pd = 0.0
        for w, r in zip(weights, self._master_scale_.rating_list):
            if start_date is None:
                start_date = self.origin
            s = start_date.to_businessdate(self.origin)
            e = end_date.to_businessdate(self.origin)
            pd += w * self._pd_curve_dict[r].get_discount_factor(s, e)
            return pd


class CreditMarkovChain(DefaultProbability):
    """ Homogeneous, discrete Credit Markov Chain """

    def __init__(self, object_name_str=''):
        super(CreditMarkovChain, self).__init__(object_name_str)
        d = [[' ', 'A', 'B', 'C', 'D'],
             ['A', 0.7, 0.2, 0.099, 0.001],
             ['B', 0.2, 0.5, 0.29, 0.01],
             ['C', 0.1, 0.2, 0.6, 0.1],
             ['D', 0.0, 0.0, 0.0, 1.0]]
        self._migration_matrix_ = DataRange(d)
        self._frequency_ = Annually()

        self._migration_matrix = None
        self._pd_vector_list = list()
        self._rebuild_object()

    def _rebuild_object(self):
        self._migration_matrix = matrix(self._migration_matrix_.item_list)

        return self

    def get_survival_probability(self, pd_value, end_date, start_date=None):
        """ returns the annualized and cumulative survival probability for a given rating resp. pd and date

        Parameters:
            pd_value (float): the current pd
            start_date (BusinessDate): date of pd observation
            end_date (BusinessDate): if given, average pd between start date (included) and end date
                                     (excluded) is given

        Returns:
            float: survival probability
        """

        weights = self._master_scale_.get_rating_weights_from_default_probability(pd_value)
        weights = matrix([list(weights)])
        if not start_date:
            start_date = self.origin
        s = start_date.to_businessdate(self.origin)
        e = end_date.to_businessdate(self.origin)
        t = businessdate.BusinessDate.diff_in_years(s, e) / self._frequency_.year_fraction
        f = int(t)
        delta = (t - f)

        if f >= 1:
            pd_until_f = weights * (self._migration_matrix ** (f - 1)) * matrix(self._master_scale_._pd_list).T
        else:
            pd_until_f = matrix(0)

        pd_from_f = weights * (self._migration_matrix ** f) * matrix(self._master_scale_._pd_list).T

        return float((1 - pd_until_f) * (1 - delta) + (1 - pd_from_f) * delta)


class ContinuousCreditMarkovChain(DefaultProbability):
    """ Homogeneous, continuous Credit Markov Chain """

    def __init__(self, object_name_str=''):
        super(ContinuousCreditMarkovChain, self).__init__(object_name_str)
        d = [[' ', 'A', 'B', 'C', 'D'],
             ['A', 0.7, 0.2, 0.099, 0.001],
             ['B', 0.2, 0.5, 0.29, 0.01],
             ['C', 0.1, 0.2, 0.6, 0.1],
             ['D', 0.0, 0.0, 0.0, 1.0]]
        self._migration_matrix_ = DataRange(d)
        self._frequency_ = Annually()

        self._generator_matrix = None
        self._pd_vector_list = list()
        self._rebuild_object()

    def _rebuild_object(self):
        _migration_matrix = matrix(list(self._migration_matrix_.item_list))
        self._generator_matrix = logm(_migration_matrix)

        return self

    def get_survival_probability(self, pd_value, end_date, start_date=None):
        """ returns the annualized and cumulative survival probability for a given rating resp. pd and date

        Parameters:
            pd_value (str/float): the current pd or rating in master scale assigned default
                                         probability object
            start_date (BusinessDate): date of pd observation
            end_date (BusinessDate): if given, average pd between start date (included) and end date
                                     (excluded) is given

        Returns:
            float: survival probability
        """

        weights = self._master_scale_.get_rating_weights_from_default_probability(pd_value)
        weights = matrix([list(weights)])

        if not start_date:
            start_date = self.origin
        s = start_date.to_businessdate(self.origin)
        e = end_date.to_businessdate(self.origin)
        t = businessdate.BusinessDate.diff_in_years(s, e) * self._frequency_.year_fraction

        if t <= 1:
            pd = t * weights * matrix(self._master_scale_.pd_list).T
        else:
            e = e.add_years(-1)
            if businessdate.BusinessDate.diff_in_years(s, e) < 0:
                e = s
            t = businessdate.BusinessDate.diff_in_years(s, e) * self._frequency_.year_fraction
            mm = expm(self._generator_matrix * t)
            pd = weights * mm * matrix(self._master_scale_.pd_list).T

        return float(1 - pd)
