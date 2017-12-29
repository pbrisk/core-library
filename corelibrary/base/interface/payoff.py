from businessdate import BusinessDate
from mitschreiben import Record

from pricing import PricingInterface


class PayOffInterface(PricingInterface):
    """ Interface declaring get_present_value using get_expected_payoff """

    def get_expected_payoff(self, value_date=BusinessDate(), index_model_dict={}):
        """ calculates expected payoff at paydate

        :param BusinessDate value_date:
        :param IndexModel index_model_dict:
        :return: float, the pv of the cash flow
        """
        raise NotImplementedError

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns present value at value_date derived by given index_models if provided

        :param value_date:
        :param index_model_dict:
        :return: float, the pv of the cash flow
        """
        payoff = self.get_expected_payoff(value_date, index_model_dict)
        df_index = self._get_discount_index(self.currency)

        pv_let = self._get_discounted_value(value_date, payoff, df_index)
        return pv_let