from businessdate import BusinessDate
from mitschreiben import Record

from corelibrary.base.baseobject import BusinessObject


class CreditExposureInterface(BusinessObject):
    """ Interface to calculate credit loss risk """

    @property
    def ccf(self):
        """ credit conversion factor """
        return self._ccf_

    @Record.Prefix()
    def get_expected_credit_exposure(self, value_date=BusinessDate(), index_model_dict={}):
        """ gets the expected credit exposure

        :param value_date:
        :param index_model_dict (optional): dict of index models incl. default loss model
        :return: float
        """
        raise NotImplementedError

    @Record.Prefix()
    def get_expected_default_loss(self, value_date=BusinessDate(), index_model_dict={}):
        """ gets the expected default loss

        :param value_date:
        :param index_model_dict (optional): dict of index models incl. default loss model
        :return: float
        """
        raise NotImplementedError

    @Record.Prefix()
    def get_expected_credit_loss(self, value_date=BusinessDate(), start_date=None, end_date=None, index_model_dict={}):
        """ gets the expected credit loss between desired dates

        :param value_date:
        :param start_date:
        :param end_date:
        :param index_model_dict (optional): dict of index models incl. default loss model
        :return: float
        """
        raise NotImplementedError
