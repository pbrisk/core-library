from businessdate import BusinessDate
from mitschreiben import Record

from corelibrary.base.baseobject import BusinessObject


class PricingInterface(BusinessObject):
    """ Interface declaring get_present_value """

    @property
    def currency(self):
        """ currency of the object """
        return self._currency_

    @Record.Prefix()
    def get_present_value(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns present value at value_date derived by given index_models if provided

        :param value_date:
        :param index_model_dict:
        :return:
        """
        raise NotImplemented

    @Record.Prefix()
    def get_positive_exposure(self, value_date=BusinessDate(), index_model_dict={}):
        """ returns positive exposure, i.e. max(0.,pv), at value_date

        :param value_date:
        :param (dict) index_model_dict: container of IndexModels
        :return:
        """
        pay_value = self.get_present_value(value_date, index_model_dict)
        return max(pay_value, 0)

    def _get_discount_index(self, currency, default=None):
        """  index to discount cash flows in given currency

        :param currency:
        :param default:
        :return:
        """
        if currency == self._discount_index_.currency:
            return self._discount_index_
        elif default is not None:
            return default

        msg = 'Missing DisountIndex in currency ' + str(currency) + ' of product ' + str(self)
        msg += '. Found only ' + str(self._discount_index_) + ' in currency ' + str(self._discount_index_.currency)
        raise Exception(msg)

    def _get_fx_index(self, currency, default=None):
        """ The FX index to convert a cash payment in the given currency to the currency of this product.

        :param currency:
        :param default: returned if no index found
        :return:
        """
        if currency == self.currency:
            return None
        elif currency == self._f_x_index_.foreign_currency:
            return self._f_x_index_
        elif default is not None:
            return default

        raise Exception("Missing FXIndex(FOR=" + str(currency) + ", DOM=" + str(self.currency) + ") of product " +
                        self.object_name + " to convert payments.")

    def _get_present_value_sum(self, pricer_list, value_date, index_model_dict):
        """ adds present values in self.currency for each item in the given pricer_list

        :param pricer_list:
        :param value_date:
        :param index_model_dict:
        :return:
        """
        ret = 0.0
        for item in pricer_list:
            fx_index = self._get_fx_index(item.currency)
            fx = fx_index.get_value(value_date) if fx_index else 1.0
            pv = item.get_present_value(value_date, index_model_dict)
            ret += fx * pv
        return ret

    def _get_discounted_value(self, value_date, payoff, discount_index, pay_date=None):
        """ discounts the payoff by discount_index values

        :param value_date:
        :param payoff:
        :param discount_index:
        :param pay_date:
        :return:
        """
        if pay_date is None:
            pay_date = self.pay_date
        df = discount_index.get_value(pay_date, value_date)
        pv_let = df * payoff

        Record(
            pay_off=payoff,
            pv_let=pv_let,
            disc_fact=df,
            disc_index=str(discount_index),
            pay_date=self.pay_date
        )

        return pv_let


