# coding=utf-8
""" module containing base object classs like VisibleObject, VisibleObjectList, AttributeList and DataRange """
import datetime
import json
import logging

from businessdate import BusinessDate, BusinessPeriod
from unicum import VisibleAttributeList as attributelist
from unicum import VisibleDataRange as datarange
from unicum import VisibleObject as visibleobject
from unicum import VisibleObjectList as objectlist
from unicum.decode_json import decode_dict as _decode_dict
from unicum.json_writer import JSONWriter as _json_writer

from corelibrary.base.namedobject import Currency

from ranger import range_from_dict, dict_from_range

core_log = logging.getLogger('corelibrary')

LIBRARY_VERSION = 'corelibrary 0.2 dev, initial development, 2017-06-31'
_order = ["Name", "Class", "Module", "Currency", "Origin", "Notional"]


class VisibleObject(visibleobject):
    """ fundamental base class with various persistence creator methods """
    __factory = dict()
    __link = dict()
    __map = {
        'ObjectFolder': 'Folder',
        'ObjectName': 'Name',
        'ObjectOrigin': 'Origin',
        'Legs': 'LegList',
        'CashFlowList': 'CashflowList',
        'ForwardVolatility': 'Volatility',
        'Rsquared': 'RSquared',
        'PiTDefaultProbability': 'PitDefaultProbability',
        'TtCDefaultProbability': 'TtcDefaultProbability',
        'YieldCurve': 'Curve',
        'FlatLGD': 'FlatLgd',
        'SetDate': 'ResetDate',
        'AssetIndex': 'SimpleAssetIndex',
        'UpdateTime': 'OriginTime',
    }

    @classmethod
    def _to_visible(cls, property_name):
        """ MyProp -> _my_prop_ """
        if isinstance(property_name, list):  # vectorize
            return [cls._to_visible(p) for p in property_name]
        if property_name in cls.__map:
            property_name = cls.__map[property_name]
        return super(VisibleObject, cls)._to_visible(property_name)

    @classmethod
    def _from_visible(cls, property_name):
        """ _my_prop_ -> MyProp """
        if isinstance(property_name, list):  # vectorize
            return [cls._from_visible(p) for p in property_name]
        return super(VisibleObject, cls)._from_visible(property_name)

    @property
    def object_name(self):
        return self._name_

    @property
    def folder(self):
        return self._folder_

    @property
    def origin(self):
        return self._origin_

    @property
    def currency(self):
        return self._currency_

    @property
    def domain(self):
        """ all relevant dates """
        return list()

    def __init__(self, object_name_str=''):
        super(VisibleObject, self).__init__(object_name_str)
        self._folder_ = '/'
        self._origin_ = BusinessDate()
        self._currency_ = Currency()
        self._libraryversion = LIBRARY_VERSION

    def __copy__(self):
        return self.__class__.from_serializable(self.to_serializable())

    def __deepcopy__(self, memo):
        serializable = self.to_serializable()
        for k in serializable:
            serializable[k] = type(serializable[k])(serializable[k])
        return self.__class__.from_serializable(self.to_serializable())

    def _cast_to_dates(self, *in_date):
        ret = list()
        r = None
        for d in in_date:
            if isinstance(d, BusinessDate):
                r = d
            else:
                if isinstance(d, (datetime.date, datetime.datetime)):
                    r = BusinessDate.from_date(d)
                elif isinstance(d, BusinessPeriod):
                    r = d.to_businessdate(self.origin)
            ret.append(r)
        return ret

    @classmethod
    def create(cls, object_name_str='', register_flag=False, **kwargs):
        obj = cls(object_name_str)
        if register_flag:
            obj.register()
        obj.modify_object(kwargs)
        return obj

    @classmethod
    def list(cls):
        func = (lambda x: x.is_modified)
        return cls.filter(func)

    # --- visible methods ---

    @classmethod
    def from_serializable(cls, object_dict, register_flag=False):
        """ corelibrary class method to create visible objects from a dictionary """

        old_key_class = 'ObjectType'
        old_key_module = 'ObjectClass'
        old_key_name = 'ObjectName'

        key_class = cls._from_visible(cls.STARTS_WITH + 'class' + cls.ENDS_WITH)
        key_module = cls._from_visible(cls.STARTS_WITH + 'module' + cls.ENDS_WITH)
        key_name = cls._from_visible(cls.STARTS_WITH + 'name' + cls.ENDS_WITH)

        old_class = object_dict.pop(old_key_class) if old_key_class in object_dict else 'VisibleObject'
        old_module = 'corelibrary.' + object_dict.pop(old_key_module) if old_key_module in object_dict else 'corelibrary'
        old_name = object_dict.pop(old_key_name) if old_key_name in object_dict else ''

        obj_class = object_dict.pop(key_class) if key_class in object_dict else old_class
        obj_module = 'corelibrary.' + object_dict.pop(key_module) if key_module in object_dict else old_module
        obj_name = object_dict.pop(key_name) if key_name in object_dict else old_name

        # obj = cls._from_class(obj_class, obj_module.lower(), obj_name)
        if register_flag and obj_name in cls.keys():
            old_obj = cls(obj_name)
            if not old_obj.__class__.__name__ == obj_class:  # todo: better check if inherited ??
                old_obj.remove()

        obj = cls._from_class(obj_class, 'corelibrary', obj_name)
        if register_flag:
            obj.register()

        # --- help to remove empty DetailList properties ---
        for key, value in {'DetailList': [[]]}.items():
            if key in object_dict and object_dict[key] == value:
                object_dict.pop(key)
                # print 'removed', key, 'property of type', type(value), 'and value', o

        obj.modify_object(object_dict)
        obj.update_link()
        return obj

    @classmethod
    def load_objects_from_string(cls, json_str, register_flag=True):
        objs = json.loads(json_str, object_hook=_decode_dict)
        if isinstance(objs, list):
            return [cls.from_serializable(o, register_flag=register_flag) for o in objs]
        else:
            return [cls.from_serializable(objs, register_flag=register_flag)]

    @classmethod
    def load_objects_from_file(cls, filename=None, register_flag=True):
        with open(filename, 'r') as json_file:
            json_str = json_file.read()
        obj = cls.load_objects_from_string(json_str, register_flag=register_flag)
        if core_log.level <= 5:
            obj_list = list(obj) if isinstance(obj, list) else [obj]
            for o in obj_list:
                core_log.debug('Created object %s from file %s' % (o.object_name, filename))
        return obj

    @classmethod
    def save_objectlist_to_file(cls, obj_list, file_name=None, all_properties_flag=False):
        objlist = sorted(obj_list, key=lambda x: x.__class__.__name__)
        if not file_name:
            file_name = 'CoreObjectList.json'
        json_file = open(file_name, 'w')
        serialized_json = '[' + ',\n'.join(obj.save_object_to_string(all_properties_flag) for obj in objlist) + ']'
        json_file.write(serialized_json)
        json_file.close()
        core_log.info('Saved AttributeList to file %s' % file_name)
        return file_name

    def save_object_to_string(self, all_properties_flag=False):
        return self.to_json(all_properties_flag=all_properties_flag)

    def save_object_to_file(self, file_name=None, append_flag=False, all_properties_flag=False):

        if not file_name:
            # file_name = '%s.json'%datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = '%s.json' % self.object_name

        content = ""
        if append_flag:
            try:
                with open(file_name, "r") as json_file:
                    content = json_file.read()
                    content = content[:content.rfind("]") - len(content)] + ",\n"
            except:
                pass

        with open(file_name, 'w') as json_file:
            if not content:
                json_file.write("[")
            else:
                json_file.write(content)

            json_file.write(self.save_object_to_string(all_properties_flag))
            json_file.write("]")

        core_log.info('Saved object %s to file %s' % (self.object_name, file_name))
        return file_name

    def to_json(self, indent="\t", all_properties_flag=False):
        return super(VisibleObject, self).to_json(indent=indent,
                                                  all_properties_flag=all_properties_flag,
                                                  dumps=_json_writer.dumps,
                                                  property_order=_order)

    def make_generic(self):
        """ method needed when loading generic information """
        self._modified_members = list()
        return self

    def get_dependent_objects(self, recursive_flag=True, include_self_flag=False):
        """
        returns the dependent objects. If recursive is True,
        returns also self and the dependent objects of the dependent objects, ... in a list.
        :param recursive_flag:
        :param include_self_flag:
        :return:
        """

        def _is_contained(obj, objs):
            for o in objs:
                if obj.object_name == o.object_name:
                    return True
            return False

        def _append_not_contained(obj, objs):
            if isinstance(obj, list):
                for o in obj:
                    _append_not_contained(o, objs)
            else:
                if obj.object_name != '' and not _is_contained(obj, objs):
                    objs.append(obj)

        def _append_dependent_objects(obj, dependent_objects):
            _append_not_contained(obj, dependent_objects)
            for o in dependent_objects_list(obj):
                _append_dependent_objects(o, dependent_objects)

        def dependent_objects_list(visible_obj):
            ret = list()
            for attr in dir(visible_obj):
                if not self._is_visible(attr):
                    continue
                obj = getattr(visible_obj, attr)
                if isinstance(obj, VisibleObject):
                    _append_not_contained(obj, ret)
                elif isinstance(obj, AttributeList):
                    for o in obj:
                        d_objs = dependent_objects_list(o)
                        _append_not_contained(d_objs, ret)
            return ret

        depend_objs = dependent_objects_list(self)
        if not recursive_flag:
            return depend_objs
        ret = list() if not include_self_flag else [self]
        for obj in depend_objs:
            _append_dependent_objects(obj, ret)
        return ret

    def get_property(self, property_name, property_item_name=None):
        if not self.__class__._is_visible(property_name):
            property_name = self.__class__._to_visible(property_name)
        if property_item_name is None:
            return getattr(self, property_name)
        raise NotImplementedError


class BusinessObject(VisibleObject):
    """ base class for business objects """
    pass


class AnalyticsObject(VisibleObject):
    """ base class for analytics objects """

    def __init__(self, object_name_str=''):
        super(AnalyticsObject, self).__init__(object_name_str)
        self._origin_time_ = '0'  # todo: use structured datetime object class


class VisibleFloat(VisibleObject):
    """ VisibleObject which is also a float. Useful to have Price or SpotFxRates to be VisibleObjects. """

    @property
    def value(self):
        return self._value_

    def __init__(self, object_name_str=''):
        super(VisibleFloat, self).__init__(str(object_name_str))
        self._value_ = 0.
        self._modified_members.append('_value_')
        if isinstance(object_name_str, str):
            if all(map(str.isdigit, tuple(object_name_str))) and len(object_name_str):
                self._value_ = float(object_name_str)
        elif isinstance(object_name_str, (int, float)):
            self._value_ = float(object_name_str)

    def to_serializable(self, level=0, all_properties_flag=False):
        if level:
            return float(self)
        else:
            return super(VisibleFloat, self).to_serializable(level, all_properties_flag)

    def conjugate(self, *args, **kwargs):  # real signature unknown
        """ Return self, the complex conjugate of any float. """
        return self.__class__(self.value.conjugate(*args, **kwargs))

    def fromhex(self, string):  # real signature unknown; restored from __doc__
        """
        float.fromhex(string) -> float

        Create a floating-point number from a hexadecimal string.
        >>> float.fromhex('0x1.ffffp10')
        2047.984375
        >>> float.fromhex('-0x1p-1074')
        -4.9406564584124654e-324
        """
        return self.__class__(self.value.fromhex(string))

    def __int__(self):
        """ x.__int__() <==> int(x) """
        return int(self.value)

    def __float__(self):
        """ x.__float__() <==> float(x) """
        return float(self.value)

    def __abs__(self):  # real signature unknown; restored from __doc__
        """ x.__abs__() <==> abs(x) """
        return self.__class__(self.value.__abs__())

    def __add__(self, y):  # real signature unknown; restored from __doc__
        """ x.__add__(y) <==> x+y """
        return self.__class__(self.value.__add__(float(y)))

    def __coerce__(self, y):  # real signature unknown; restored from __doc__
        """ x.__coerce__(y) <==> coerce(x, y) """
        return self, self.__class__(self.value.__coerce__(y))

    def __divmod__(self, y):  # real signature unknown; restored from __doc__
        """ x.__divmod__(y) <==> divmod(x, y) """
        return self.__class__(self.value.__divmod__(float(y)))

    def __div__(self, y):  # real signature unknown; restored from __doc__
        """ x.__div__(y) <==> x/y """
        return self.__class__(self.value.__div__(float(y)))

    def __floordiv__(self, y):  # real signature unknown; restored from __doc__
        """ x.__floordiv__(y) <==> x//y """
        return self.__class__(self.value.__floordiv__(float(y)))

    def __mod__(self, y):  # real signature unknown; restored from __doc__
        """ x.__mod__(y) <==> x%y """
        return self.__class__(self.value.__mod__(float(y)))

    def __mul__(self, y):  # real signature unknown; restored from __doc__
        """ x.__mul__(y) <==> x*y """
        return self.__class__(self.value.__mul__(float(y)))

    def __neg__(self):  # real signature unknown; restored from __doc__
        """ x.__neg__() <==> -x """
        return self.__class__(self.value.__neg__())

    def __pos__(self):  # real signature unknown; restored from __doc__
        """ x.__pos__() <==> +x """
        return self.__class__(self.value.__pos__())

    def __pow__(self, y, z=None):  # real signature unknown; restored from __doc__
        """ x.__pow__(y[, z]) <==> pow(x, y[, z]) """
        return self.__class__(self.value.__pow__(float(y), z))

    def __radd__(self, y):  # real signature unknown; restored from __doc__
        """ x.__radd__(y) <==> y+x """
        return self.__class__(self.value.__radd__(float(y)))

    def __rdivmod__(self, y):  # real signature unknown; restored from __doc__
        """ x.__rdivmod__(y) <==> divmod(y, x) """
        return self.__class__(self.value.__rdivmod__(float(y)))

    def __rdiv__(self, y):  # real signature unknown; restored from __doc__
        """ x.__rdiv__(y) <==> y/x """
        return self.__class__(self.value.__rdiv__(float(y)))

    def __rfloordiv__(self, y):  # real signature unknown; restored from __doc__
        """ x.__rfloordiv__(y) <==> y//x """
        return self.__class__(self.value.__rfloordiv__(float(y)))

    def __rmod__(self, y):  # real signature unknown; restored from __doc__
        """ x.__rmod__(y) <==> y%x """
        return self.__class__(self.value.__rmod__(float(y)))

    def __rmul__(self, y):  # real signature unknown; restored from __doc__
        """ x.__rmul__(y) <==> y*x """
        return self.__class__(self.value.__rmul__(float(y)))

    def __rpow__(self, x, z=None):  # real signature unknown; restored from __doc__
        """ y.__rpow__(x[, z]) <==> pow(x, y[, z]) """
        return self.__class__(self.value.__rpow__(float(x), z))

    def __rsub__(self, y):  # real signature unknown; restored from __doc__
        """ x.__rsub__(y) <==> y-x """
        return self.__class__(self.value.__rsub__(float(y)))

    def __rtruediv__(self, y):  # real signature unknown; restored from __doc__
        """ x.__rtruediv__(y) <==> y/x """
        return self.__class__(self.value.__rtruediv__(float(y)))

    def __sub__(self, y):  # real signature unknown; restored from __doc__
        """ x.__sub__(y) <==> x-y """
        return self.__class__(self.value.__sub__(float(y)))

    def __truediv__(self, y):  # real signature unknown; restored from __doc__
        """ x.__truediv__(y) <==> x/y """
        return self.__class__(self.value.__truediv__(float(y)))

    def __trunc__(self, *args, **kwargs):  # real signature unknown
        """ Return the Integral closest to x between 0 and x. """
        return self.__class__(self.value.__trunc__(*args, **kwargs))


class AttributeList(attributelist):
    """ object list class """

    def __reduce__(self):
        return self.__class__, (list(self),)

    def __init__(self, iterable=None, object_type=VisibleObject,
                 value_types=(float, int, str, type(None), VisibleObject)):
        super(AttributeList, self).__init__(iterable, object_type, value_types)


class ObjectList(objectlist):
    """ object list class """

    def __init__(self, iterable=None, object_type=VisibleObject):
        if iterable and not all(isinstance(i, object_type) for i in iterable):
            if all(isinstance(i, list) for i in iterable):
                if len(iterable[0]) == 1:
                    # May be we got a nested list
                    iterable = [i[0] for i in iterable]

            if all(isinstance(i, list) for i in iterable):
                # May be we are dealing with some legacy AttributeList
                iterable = AttributeList(iterable)
            else:
                iterable = [VisibleObject(i) for i in iterable]
        super(ObjectList, self).__init__(iterable, object_type)


class DataRange(datarange):
    """ DataRange class """

    def __str__(self):
        return 'DataRange(%s)' % str(list(self))

    def get_column(self, col_index):
        return self.col(col_index)

    def get_row(self, row_index):
        return self.row(row_index)

    def get_item(self, row_index=None, col_index=None):
        return self[row_index, col_index]


class DataTable(DataRange):
    """ Data Table class """

    def __init__(self, items=None):
        super(DataTable, self).__init__(items, (float, int, str, type(None)))

    def __reduce__(self):
        return self.__class__, (self.total_list,)


class VisibleList(VisibleObject):
    """ VisibleList class """

    @classmethod
    def create_from_cache(cls, object_name_str=''):
        """
        creates VisibleList containing all VisibleObjects in object cache
        :param object_name_str:
        :return:
        """
        cache = VisibleObject.values()
        visible_list = cls(object_name_str)
        if object_name_str:
            visible_list.register()
        visible_list.build_from_list(cache)
        return visible_list

    def __init__(self, object_name_str=''):
        """
        container for VisibleObjects
        :param object_name_str: VisibleList object name

        VisibleList admit a bulk create and modify for VisibleObjects as long on restricts to simple properties.
        """
        self._list_type = self._list_type if hasattr(self, '_list_type') else VisibleObject,
        self._list_module = self._list_module if hasattr(self, '_list_module') else VisibleObject.__class__.__module__

        super(VisibleList, self).__init__(object_name_str)

        for attr in dir(self._list_module):
            cls_type = getattr(self._list_module, attr)
            if isinstance(cls_type, type) and issubclass(cls_type, self._list_type):
                setattr(self, self.__class__._to_visible(cls_type.__name__), AttributeList())

    def build_from_list(self, object_list=list()):
        """

        :param object_list:
        :return:
        """
        for obj in object_list:
            if isinstance(obj, VisibleObject):
                visible_name = self.__class__._to_visible(obj.__class__.__name__)
                if hasattr(self, visible_name):
                    attr = getattr(self, visible_name)
                    attr.append(obj)
                    self.modify_object(visible_name, attr)
        return self
