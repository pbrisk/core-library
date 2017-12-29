# coding=utf-8
"""
fx vol module
"""
import operator

from businessdate.businessdate import BusinessPeriod
from dcf.interpolation import linear
from putcall.optionvaluator import OptionValuatorLN
from unicum.datarange import DataRange

from corelibrary.base.baseobject import DataTable
from corelibrary.base.namedobject import EUR, USD

from basevol import ImpliedVol


class FxVol(ImpliedVol):
    """ FxVol """
    def __init__(self, object_name_str=''):
        super(FxVol, self).__init__(object_name_str)
        self._for_curr_ = EUR()
        self._dom_curr_ = USD()
        self._curr_pair_ = "EUR/USD"  # todo: either define NamedObject on CurrPair or better us _for/_dom
        self._strike_curr_ = USD()
        self._delta_type_ = "Spot"
        self._strike_type_ = "Absolute"
        self._option_pricer = OptionValuatorLN()


class StrikeVol(FxVol):
    """ StrikeVol """

    class SurfaceFromInstrumentsBuilder(object):
        """" _ """

        def __init__(self, instruments):
            self._instruments = instruments

        def build_surface(self):
            all_strikes = sorted(self._instruments.col("Strike"))
            strikes = all_strikes  # get_grid(min(all_strikes), max(all_strikes), 20)
            strikevols_per_tenor = self._get_strikevols_per_expiry_tenor()
            interpolators = self._get_interpolators(strikevols_per_tenor)
            rows = self._interpolate(strikes, interpolators)
            data_table = DataTable(rows)
            return data_table

        def _interpolate(self, all_strikes, interpolators):
            header = [None] + [s for s in all_strikes]
            rows = [header] + [[expiry] + [interpol(strike) for strike in all_strikes] for expiry, interpol in
                               interpolators]
            # for expiry, interpol in interpolators:
            #    row = [expiry] + [interpol(strike) for strike in all_strikes]
            #    rows.append(row)
            # header = [None] + [s for s in all_strikes]
            # rows.insert(0, header)
            return rows

        def _get_interpolators(self, strikevols_per_tenor):
            ret = []
            for expiry, strikes, vols in strikevols_per_tenor:
                ret.append((expiry, linear(strikes, vols)))
            return ret

        def _get_strikevols_per_expiry_tenor(self):
            expiries = self._instruments.col("Expiry")
            strikes = self._instruments.col("Strike")
            vols = self._instruments.col("Vol")
            n = len(expiries)
            values_dict = {}
            for i in xrange(n):
                expiry = BusinessPeriod(expiries[i])
                if not expiry in values_dict:
                    values_dict[expiry] = ([], [])
                values_dict[expiry][0].append(strikes[i])
                values_dict[expiry][1].append(vols[i])
            # convert the values dict to a list of triple sorted by expiry
            ret = []
            for expiry, strikevols in values_dict.items():
                ret.append((expiry, strikevols[0], strikevols[1]))
            ret = sorted(ret, key=operator.itemgetter(0))
            return ret

    def __init__(self, object_name_str=''):
        super(StrikeVol, self).__init__(object_name_str)
        self._instruments_ = DataRange()

    def _rebuild_object(self):
        if (not '_surface_' in self._modified_members) and'_instruments_' in self._modified_members:
            self._surface_ = self._build_surface_from_instruments()
        return super(StrikeVol, self)._rebuild_object()

    def _build_surface_from_instruments(self):
        sb = StrikeVol.SurfaceFromInstrumentsBuilder(self._instruments_)
        ret = sb.build_surface()
        return ret


class DeltaVol(FxVol):
    """ DeltaVol """
    pass


class MalzVol(FxVol):
    """ MalzVol """
    pass
