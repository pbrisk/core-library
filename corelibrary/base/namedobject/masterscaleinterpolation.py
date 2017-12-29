# coding=utf-8
"""
module containing master scale state interpolation classes
"""
from unicum import FactoryObject


class MasterScaleInterpolation(FactoryObject):
    """ master scale state interpolation class """
    __factory = dict()

    def __init__(self, *args):  # pylint: disable=unused-argument
        super(MasterScaleInterpolation, self).__init__()

    def get_rating_weight_list(self, pd_boundary_list, pd_value):
        """

        :param pd_boundary_list:
        :param pd_value:
        :return:
        """
        pass


class Bucketing(MasterScaleInterpolation):
    """ master scale state interpolation class by bucketing """

    def get_rating_weight_list(self, pd_value, pd_boundary_list):
        """

        :param pd_value:
        :param pd_boundary_list:
        :return:
        """
        assert 0.0 <= pd_value <= 1.0, 'rating float must be between 0.0 and 1.0 but was %f' % pd_value
        if min(pd_boundary_list) > 0.0:
            pd_boundary_list.append(0.0)
        if max(pd_boundary_list) < 1.0:
            pd_boundary_list.append(1.0)
        assert max(pd_boundary_list) == 1.0 and min(
            pd_boundary_list) == 0.0, 'boundary list must consist values between 0.0 and 1.0'
        position = len([x for x in pd_boundary_list if x <= pd_value])
        position = min(position, len(pd_boundary_list) - 1) - 1
        weight_list = [0.0] * (len(pd_boundary_list) - 1)
        weight_list[position] = 1.0
        return weight_list


class NeighbourhoodInterpolation(MasterScaleInterpolation):
    """ master scale state interpolation class by neighbourhoods """

    def get_rating_weight_list(self, pd_value, pd_boundary_list):
        """

        :param pd_value:
        :param pd_boundary_list:
        :return:
        """
        ceiling_index = None
        assert 0.0 <= pd_value <= 1.0, \
            'rating float must be between 0.0 and 1.0 but was %f' % pd_value
        if min(pd_boundary_list) > 0.0:
            pd_boundary_list.insert(0, 0.0)
        if max(pd_boundary_list) < 1.0:
            pd_boundary_list.append(1.0)
        assert max(pd_boundary_list) == 1.0 and min(pd_boundary_list) == 0.0, \
            'pd list must consist values between 0.0 and 1.0'

        weight_list = [0.0] * (len(pd_boundary_list) - 1)
        if pd_boundary_list.count(pd_value):
            weight_list[min(len(weight_list) - 1, pd_boundary_list.index(pd_value))] = 1.0
        else:
            ceiling_index = [x <= pd_value for x in pd_boundary_list].index(False)
            floor_index = ceiling_index - 1

            if len(weight_list) - 1 >= ceiling_index:
                pd_cap = pd_boundary_list[ceiling_index]
                pd_floor = pd_boundary_list[floor_index]

                weight_list[floor_index] = (pd_value - pd_cap) / (pd_floor - pd_cap)
                weight_list[ceiling_index] = 1 - weight_list[floor_index]
            else:
                weight_list[len(weight_list) - 1] = 1.0

        if ceiling_index == 0:
            weight_list[0] = 1

        return weight_list


# register instances

Bucketing().register()
NeighbourhoodInterpolation().register()
