# coding=utf-8
"""
module containing master scale classes
"""
from corelibrary.base.baseobject import DataRange
from corelibrary.base.interface.masterscale import MasterScaleInterface
from corelibrary.base.namedobject import NeighbourhoodInterpolation, Bucketing


class MasterScale(MasterScaleInterface):
    r"""
    MasterScale root class stating data on rating classes
    Basic model is a state space $S$ spanned by finite many rating classes $R_i, i = 1 \dots n$.
    The classes are given by a master scale and represent the {\em pure states} $b_i%,
    which form a real numbered valued basis of $S$.
    """

    def __init__(self, object_name_str=''):
        super(MasterScale, self).__init__(object_name_str)
        # :param (MasterScaleInterpolation) StateInterpolation method to interpolate states
        self._state_interpolation_ = NeighbourhoodInterpolation()
        # :param (MasterScaleInterpolation) Mapping method to derive a single rating of a given pd
        self._mapping_ = Bucketing()
        # :param (DataRange) MasterScale data table defining rating classes resp. pure states
        self._master_scale_ = DataRange([['', 'DefaultProbability', 'UpperBound', 'LowerBound'],
                                         ['A', 0.001, 0.005, 0.000],
                                         ['B', 0.01, 0.10, 0.005],
                                         ['C', 0.1, 1.000, 0.10],
                                         ['D', 1.0, 1.000, 1.000]])
        self._rating_list = list()
        self._pd_list = list()
        self._master_scale_dict = dict()
        self._boundary_list = list()
        self._fallback_rating_ = self._master_scale_.row_keys()[-2]

        self._rebuild_object()

    def __nonzero__(self):
        return self._master_scale_.__len__() > 0

    def _rebuild_object(self):
        col_header_list = self._master_scale_.col_keys()
        rating_list = self._master_scale_.row_keys()
        assert len(set(rating_list)) == len(rating_list)
        pd_list = self._master_scale_.get_column('DefaultProbability')
        bound_list = list()
        if col_header_list.count('LowerBound'):
            bound_list = self._master_scale_.get_column('LowerBound')
            bound_list.append(1.0)
        elif col_header_list.count('UpperBound'):
            bound_list = [0.0]
            bound_list.extend(self._master_scale_.get_column('UpperBound'))
        else:
            bound_list = [0.0]
            for u, l in zip(pd_list[1:], pd_list[:-1]):
                if u < 1:
                    bound_list.append((u + l) * 0.5)
                else:
                    bound_list.append(u)
            bound_list.append(1.0)
        self._rating_list = list(rating_list)
        self._pd_list = list(pd_list)
        self._master_scale_dict = dict()
        for k, v in zip(rating_list, pd_list):
            self._master_scale_dict[k] = v
        self._boundary_list = bound_list

        self._fallback_rating_ = self._master_scale_.row_keys()[-2]

    def get_default_probability_from_rating(self, rating_str):
        """ returns the default probability from a rating

        Parameters:
            rating_str (string): rating as string

        Returns:
            float: default probability according to given rating
        """

        pd_value = rating_str
        if isinstance(rating_str, str):
            pd_value = self._master_scale_dict[rating_str]
        assert isinstance(pd_value, float), \
            'rating must be masterscale matching string or float but was %s' % str(type(rating_str))
        assert 0.0 <= pd_value <= 1.0, 'rating float must be between 0.0 and 1.0 but was %f' % pd_value
        return pd_value

    def get_rating_from_default_probability(self, pd_value):
        """ returns the rating given a pd value

        Parameters:
            pd_value (float): value of default probability

        Returns:
            string: assessed rating according to given default probability
        """

        rating_str = pd_value
        if isinstance(pd_value, float):
            weight_list = self.get_rating_weights_from_default_probability(pd_value)
            rating_str = self._rating_list[weight_list.index(max(weight_list))]
        assert self._rating_list.count(rating_str) == 1, \
            'pd must be float or masterscale matching string but was %s' % str(type(rating_str))
        return rating_str

    def get_rating_weights_from_default_probability(self, pd_value):
        """ returns the weights of each rating based on the default probability

        Parameters:
            pd_value (float): pd value for which weights need to be assessed
        Returns:
            list:    rating weights of the masterscale
        """
        weights = [0.0] * len(self._rating_list)
        weights = self._mapping_.get_rating_weight_list(pd_value, self._boundary_list)
        return weights
