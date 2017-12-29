# coding=utf-8

from businessdate import BusinessDate, BusinessSchedule

from corelibrary.base.baseobject import ObjectList
from corelibrary.base.namedobject.compounding import Continuous
from corelibrary.base.namedobject.frequency import Quarterly
from corelibrary.base.namedobject.daycount import ActAct
from corelibrary.base.namedobject.optionpayoff import Call
from corelibrary.base.interface.credit import CreditExposureInterface
from corelibrary.base.interface.index import IndexInterface
from corelibrary.business.index import CreditIndex


class Engagement(CreditExposureInterface):
    """ Engagement consists Contract and Collateral by netting agreement """

    def __init__(self, object_name_str=''):
        super(Engagement, self).__init__(object_name_str)
        self._contract_list_ = ObjectList()
        self._collateral_list_ = ObjectList()
        self._ecl_frequency_ = Quarterly()

        self._effective_rate = 0.
        self._credit_index = CreditIndex()

    def get_positive_exposure(self, value_date=BusinessDate(), index_model_dict={}):
        """ gets the positive exposure of a contract

        :param value_date: the value date of the contract
        :param index_model_dict: dict of IndexModels
        :return: positive exposure at value_date

        """
        return sum(c.get_positive_exposure(value_date, index_model_dict) for c in self._contract_list_)

    def get_expected_credit_loss(self, value_date=BusinessDate(), start_date=None, end_date=None, index_model_dict={}):
        """ gets the expected credit loss between desired dates

        :param value_date:
        :param start_date:
        :param end_date:
        :param index_model_dict (optional): dict of index models incl. default loss model
        :return: float
        """

        if not end_date:
            end_date = max(c.maturity for c in self._contract_list_)
        end_date = end_date.to_businessdate(self.origin)

        if not start_date:
            start_date = self.origin
        start_date = start_date.to_businessdate(self.origin)

        freq = self._ecl_frequency_.period
        schedule = BusinessSchedule(start_date, end_date, freq, start_date)

        dcc = ActAct()
        total_ecl = 0.0
        for loop_date, e in zip(schedule[:-1], schedule[1:]):
            df = Continuous().disc_factor_from_rate(start_date, loop_date, dcc, self._effective_rate)
            svp = self._survival_index.get_value(loop_date)
            yf = BusinessDate.diff_in_years(loop_date, e)
            fwd = 1 - self._survival_index.get_value(e, loop_date)
            loss = self.get_expected_default_loss(loop_date, index_model_dict)
            ecl = df * svp * yf * fwd * loss
            total_ecl += ecl

        return total_ecl


# simple netting -------------------------------------------------------------

class SimpleSecuredDefaultLossModel(Engagement):
    """ going and gone scenario loss model """

    def __init__(self, object_name_str=''):
        super(SimpleSecuredDefaultLossModel, self).__init__(object_name_str)
        self._lgd_ = 1.
        self._price_index_ = IndexInterface()

    def _get_recovery_call_spread(self, strike, value_date=BusinessDate(), index_model_dict={}):
        """

        :param strike:
        :param value_date:
        :param index_model_dict:
        :return:
        """
        pv = sum(c.get_present_value(value_date, index_model_dict) for c in self._collateral_list_)
        if not pv:
            return 0.

        index_model = index_model_dict.get(self._rate_index_.object_name, self._price_index_.index_model)

        prior_change = sum(c.prior_change for c in self._collateral_list_)
        max_claim = sum(c.max_claim for c in self._collateral_list_)

        iv = index_model.get_value(self._price_index_, value_date)

        low_strike = prior_change
        low_strike *= iv/pv
        high_strike = prior_change + min(strike, max_claim)
        high_strike *= iv/pv

        collateral_value = 0.
        collateral_value += index_model.get_option_payoff_value(self._price_index_, Call(), low_strike, value_date)
        collateral_value -= index_model.get_option_payoff_value(self._price_index_, Call(), high_strike, value_date)

        return collateral_value * pv

    def get_expected_default_loss(self, value_date=None, index_model_dict={}):
        """

        :param value_date:
        :param index_model_dict:
        :return:
        """
        ead = self.get_positive_exposure(value_date)
        rec = self._get_recovery_call_spread(ead, value_date, index_model_dict)
        return (ead - min(ead, rec)) * self._lgd_


class GoingGoneDefaultLossModel(Engagement):
    """ going and gone scenario loss model """

    def __init__(self, object_name_str=''):
        super(GoingGoneDefaultLossModel, self).__init__(object_name_str)
        self._recovery_cost_rate_ = 0.
        self._resolution_probability_ = 1.

    def _get_going_loss(self, value_date=None, index_model_dict={}):
        ead = self.get_positive_exposure(value_date)
        return ead * self._recovery_cost_rate_

    def _get_gone_loss(self, value_date=None, index_model_dict={}):
        return super(GoingGoneDefaultLossModel, self).get_expected_default_loss(value_date, index_model_dict)

    def get_expected_default_loss(self, value_date=None, index_model_dict={}):
        r""" Calculates the expected default loss

        Parameters:
            value_date (BusinessDate): date of the valuation
            index_model_dict (dict): dict of IndexModels

        Returns:
            float: expected default loss value

        For the calculate the expected default loss two scenarios are distinguished:

        1. Going scenario (or 'Nicht Verwertung'):

            The going loss is defined as

            .. math::
                Going =  (q_{k} + q_{v}) \cdot EAD

            with :math:`q_{k}` is the direct cost factor, :math:`q_{v}` the waiver factor and :math:`EAD` is the
            exposure at default.

        2. Gone scenario (or 'Abwicklung'):

            The gone loss is defined as

            .. math::
                :nowrap:

                \[
                    Gone = \frac{1}{(1 + z_{eff})^{\Delta t}}
                        \left[
                                EAD \cdot
                                \left((1 + z_{eff})^{\Delta t}-1 \right) + (1 - q_u)  \cdot
                                \left ( A - \min\left(\sum_{j \in \text{Collaterals}} S^*_j,A \right ) \right )
                        \right]
                \]

            where :math:`A = EAD + K + Z`, with :math:`K = q_k \cdot EAD`, :math:`Z= q_z \cdot (ZL - EAD)`,
            and :math:`q_u` describe the unsecured proceeds.
            Additionally, :math:`S^*_j= \max(q_{s,j} S_j-V_j,0)` is the positive forward
            collateral value at valuation date :math:`t` with secured proceed factor
            (recovery rate) :math:`q_j`, excluding prior charge :math:`V_j`,
            for collateral :math:`j`.

        As a result the expected default loss is finally calculated as

        .. math::
            :nowrap:

            \[
                \text{EDL} = \frac{\sum_{i \in \text{DefaultScenarios}}
                             \left[ (1 - P_i) \cdot Going + P_i \cdot Gone \right] \cdot w_i}
                             {\sum_{i \in \text{DefaultScenarios}}w_i}
            \]

        where :math:`w_i` is the weight and :math:`P_i` is the probability of resolution for each scenario.
        """

        # prob weighted loss
        res_prob = self._resolution_probability_
        going = self._get_going_loss(value_date, index_model_dict)
        gone = self._get_gone_loss(value_date, index_model_dict)

        loss = (1 - res_prob) * going + res_prob * gone
        # return self._allocation_.get_allocated_default_loss(self, expected_default_loss, value_date)
        return loss


class SimpleDefaultLossModel(GoingGoneDefaultLossModel):
    """ SimpleDefaultLossModel collateral agreement"""

    def __init__(self, object_name_str=''):
        super(SimpleDefaultLossModel, self).__init__(object_name_str)
        self._unsecured_proceed_ = 0.
        self._direct_cost_factor_ = 0.
        self._resolution_cost_factor_ = 0.
        self._resolution_probability_ = 0.
        self._waiver_factor_ = 0.
        self._time_in_non_resolution_ = 0.
        self._time_in_resolution_ = 0.
        self._draw_after_default_factor_ = 0.

        self._max_claim_ = 0.  # todo move to something like collateral agreement?
        self._prior_charge_ = 0.  # todo move to something like collateral agreement?
        self._approved_amount_ = 0.  # todo move to something like contract?
        self._effective_rate_ = 0.  # todo read from contract?

        self._price_index_ = IndexInterface()

    def _get_going_loss(self, value_date=None, index_model_dict={}):

        r_eff = self.effective_rate
        ead = self.get_positive_exposure(value_date)

        # going case
        time_in_nonres = self._time_in_non_resolution_
        direct_cost_factor = self._direct_cost_factor_
        waiver_factor = self._waiver_factor_

        df_going = ((1 + r_eff) ** (-time_in_nonres))  # todo use dcf
        going = ead * (direct_cost_factor + waiver_factor) * df_going

        return going

    def _get_gone_loss(self, value_date=None, index_model_dict={}):

        r_eff = self.effective_rate
        ead = self.get_positive_exposure(value_date)

        # claim
        res_cost_factor = self._resolution_cost_factor_
        dad_factor = self._draw_after_default_factor_
        max_ead = self._approved_amount_

        claim = (1 + res_cost_factor) * (ead + dad_factor * min(max_ead - res_cost_factor, 0))

        # gone case
        time_in_res = self._time_in_resolution_
        unsecured_proceeds = self._unsecured_proceed_
        default_rec = self._get_recovery_call_spread(claim, value_date, index_model_dict)

        df_gone = (1 + r_eff) ** time_in_res  # todo use dcf
        recovery = (1 - unsecured_proceeds) * (claim - min(default_rec, claim))
        ead_at_resolution = (df_gone - 1) * ead
        gone = (ead_at_resolution + recovery) / df_gone

        return gone
