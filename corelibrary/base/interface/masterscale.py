# coding=utf-8

from corelibrary.base.baseobject import AnalyticsObject


class MasterScaleInterface(AnalyticsObject):
    """ interface for MasterScale objects """

    @property
    def fallback_rating(self):
        """ fallback rating """
        return self._fallback_rating_

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
            rating_str = self.rating_list[weight_list.index(max(weight_list))]
        assert self.rating_list.count(rating_str) == 1, \
            'pd must be float or masterscale matching string but was %s' % str(type(rating_str))
        return rating_str

    def get_rating_weights_from_default_probability(self, pd_value):
        """ returns the weights of each rating based on the default probability

        Parameters:
            pd_value (float): pd value for which weights need to be assessed
        Returns:
            list:    rating weights of the masterscale
        """
        raise NotImplementedError
