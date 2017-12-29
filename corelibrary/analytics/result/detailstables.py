from table import Table
from businessdate.businessdate import BusinessDate


class DetailsTables(object):
    def __init__(self, details_dict):
        self._DETAILS_TAB_NAME = "CashFlowDetails"
        self._details_dict = details_dict
        self._tabs = {}
        self._details_identifier = self._set_details_tables_identifier()
        self._table_names = self._set_up_tables_names()

    def _set_up_tables_names(self):
        ret = dict()
        details_header = ["cf_name", "currency", "notional", "start_date", "end_date", "pay_date", "reset_date",
                          "year_fraction", "multiplier", "index", "spread", "constant_rate",
                          "cap", "floor", "strike", "forward", "fixing_value"]
        for tab_name in self._details_identifier.values():
            ret[tab_name + "." + self._DETAILS_TAB_NAME] = details_header
        return ret


    def _set_details_tables_identifier(self):
        ret = dict()
        ret[tuple(["PayLeg"])] = "PayLeg"
        ret[tuple(["RecLeg"])] = "RecLeg"
        ret[("CapFloor", "CashFlow")] = "CapFloorLeg"
        ret[tuple(["Caplet"])] = "CapLeg"
        ret[tuple(["Floorlet"])] = "FloorLeg"
        return ret

    def build_details_tabs(self, values_in_excel_format=True):
        def _get_cf_name(i, s):
            n = s[i:i + 5]
            if n.endswith(")"):
                return n[0:3] + "0" + n[3]
            else:
                return n

        format_fct = to_excel if values_in_excel_format else lambda x : x
        format_fct_tabs = tables_to_excel if values_in_excel_format else lambda x : x
        props = []
        for keys, v in self._details_dict.items():
            s = str(keys)
            #print(s)
            tab = self._tab(keys)
            if tab is None:
                props.append((".".join([keys[0], keys[-2], keys[-1]]), format_fct(v)))
            else:
                i = s.find("CF_")
                if i > -1:
                    cf_name = _get_cf_name(i, s)
                    tab.append(cf_name, keys[-1], v)
                else:
                    tab.append(format_fct(keys[-2]), format_fct(keys[-1]), v)

        return format_fct_tabs(self._tabs), props

    def _get_table(self, tab_name):
        left_upper = self._left_upper(tab_name)
        if not tab_name in self._tabs:
            tab = Table(name=tab_name, left_upper=left_upper)
            tab.col_sorted = CmpByList(self._table_names[tab_name])
            self._tabs[tab_name] = tab
        return self._tabs[tab_name]

    def _tab(self, key):
        def _is_contained(identifier, key):
            return all([i in key for i in identifier])

        key_str = str(key)
        for identifier, tab_name_prefix in self._details_identifier.items():
            if _is_contained(identifier, key_str):
                tab_name = tab_name_prefix + "." + self._DETAILS_TAB_NAME
                return self._get_table(tab_name)
        return None

    def _left_upper(self, tab_name):
        return self._table_names[tab_name][0]


    def _disc_tab_to_dict(self, disc_tab):
        ret = dict()
        ccy_str = "pay_ccy"
        date_str = "pay_date"
        for row in disc_tab.rows():
            ccy = row[ccy_str]
            if not ccy in ret:
                ret[ccy] = dict()
            date = row[date_str]
            ret[ccy][date] = (row["disc_fact"], row["fx"])
        return ret


class CmpByList(object):
    def __init__(self, order):
        self._order = order

    def __call__(self, x):
        if x in self._order:
            return self._order.index(x)
        return 10000


def str_cmp(s):
    return hash(s)


class CmpDatesFormated(object):
    def __init__(self):
        pass

    def __call__(self, date_formated_str):
        # dd.mm.yyyy
        return int(date_formated_str[6:10]) * 10000 + int(date_formated_str[3:5]) * 100 + int(date_formated_str[0:2])


def to_excel(*props):
    def to_string(val):
        if isinstance(val, float):
            return str(val).replace(".", ",")
        elif isinstance(val, BusinessDate):
            return val.to_string("%d.%m.%Y")
        else:
            return str(val)
    properties = [to_string(p) for p in props]
    return "\t".join(properties)


def tables_to_excel(tables_dict):
    ret = dict()
    for tab_name, tab in tables_dict.items():
        ret[tab_name] = tab.unitary_operation(lambda r, c, v : to_excel(v))
    return ret
