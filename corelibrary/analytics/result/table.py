
class Table(object):
    @property
    def rows_count(self):
        return len(self.row_keys)

    @property
    def cols_count(self):
        return len(self.col_keys)

    """
    A table consist of columns and rows. Each entry has a row and a column key.
    """
    def __init__(self, default_value=None, name=None, left_upper=None):
        self.row_keys = []
        self.col_keys = []
        self._values = {}
        self._default_value = default_value
        self.name = name
        self.left_upper = left_upper
        self.row_sorted = None
        self.col_sorted = None

    def append(self, row_key, col_key, value):
        col_dict = self._values.get(row_key, None)
        if col_dict is None:
            self._values[row_key] = {col_key: value}
            self.row_keys.append(row_key)
        else:
            col_dict[col_key] = value
        if col_key not in self.col_keys:
            self.col_keys.append(col_key)

    def append_row(self, row_key, row):
        for col_key, value in row.items():
            self.append(row_key, col_key, value)

    def value(self, row_key, col_key):
        row_dict = self._values.get(row_key, None)
        if row_dict is None:
            return self._default_value
        ret = row_dict.get(col_key, self._default_value)
        return ret

    def get(self, row_key, col_key):
        return self.value(row_key, col_key)

    def __call__(self, row_key, col_key):
        return self.value(row_key, col_key)

    def get_row(self, row_key, include_row_keys=False):
        ret = {}
        if include_row_keys:
            ret[self.left_upper] = row_key
        for col_key in self.col_keys:
            ret[col_key] = self.value(row_key, col_key)
        return ret

    def get_row_list(self, row_key, col_keys):
        """
        returns the values of the row:row_key for all col_keys.
        """
        return [self(row_key, col_key) for col_key in col_keys]

    def rows(self, include_row_keys=False):
        """
        returns the table as list of row dicts
        :return:
        """
        ret = []
        for row_key in self.row_keys:
            ret.append(self.get_row(row_key, include_row_keys))
        return ret

    def get_column(self, col_key):
        ret = {}
        for row_key in self.row_keys:
            ret[row_key] = self.value(row_key, col_key)
        return ret

    def get_default(self):
        return self._default_value

    def contains(self, row_key, col_key):
        if row_key in self._values.keys():
            colDict = self._values[row_key]
            if col_key in colDict.keys():
                if colDict[col_key] != self._default_value:
                    return True
                    # if row_key in self.row_keys and col_key in self.col_keys:
                    # if self._values[row_key][col_key] != self._default_value:
                    # return True
        return False

    def sort(self, row_compare=None, column_compare=None):
        ret = Table(name=self.name, left_upper=self.left_upper, default_value=self._default_value)
        sortrow_keys = sorted(self.row_keys, key=row_compare)
        sortcol_keys = sorted(self.col_keys, key=column_compare)
        for row_key in sortrow_keys:
            for col_key in sortcol_keys:
                ret.append(row_key, col_key, self.value(row_key, col_key))

        return ret

    def __iter__(self):
        return Table.TableIterator(self)

    class TableIterator(object):
        def __init__(self, table):
            self.table = table
            self.nRow = len(table.row_keys)
            self.nCol = len(table.col_keys)
            self.r = 0
            self.c = 0

        def next(self):
            if self.c >= self.nCol:
                raise StopIteration
            rkey = self.table.row_keys[self.r]
            ckey = self.table.col_keys[self.c]
            v = self.table.value(rkey, ckey)
            if self.r < self.nRow - 1:
                self.r += 1
            else:
                self.r = 0
                self.c += 1

            return rkey, ckey, v

        def __next__(self):
            return self.next()

    def operation(self, table, fct):
        ret = Table(name=self.name, left_upper=self.left_upper, default_value=self._default_value)
        for r, c, v in self:
            v2 = table.value(r, c)
            if v2 != table.getDefault():
                v3 = fct(r, c, v, v2)
                ret.append(r, c, v3)
        return ret

    def unitary_operation(self, fct):
        ret = Table(name=self.name, left_upper=self.left_upper, default_value=self._default_value)
        for r, c, v in self:
            if v != self._default_value:
                w = fct(r, c, v)
                ret.append(r, c, w)
        return ret

    def modify_keys(self, row_fct=lambda x: x, col_fct=lambda x: x):
        ret = Table(name=self.name, left_upper=self.left_upper, default_value=self._default_value)
        for r, c, v in self:
            ret.append(row_fct(r), col_fct(c), v)
        return ret

    def aggregation(self, value_fct=lambda x : x):
        """
        Calculates the sum of the table not None entries using the value_fct, i.e. sum(f(v)).
        Returns the sum and the number of not None entries.
        """
        ret = 0.0
        n = 0
        for r, c, v in self:
            if v != self._default_value:
                n += 1
                ret = ret + value_fct(v)
        return ret, n

    def repr(self, left_upper=None, tab_name=None):
        # def table(self, table, leftUpper="LeftUpper", tabName=None):
        representation = []
        if len(self.row_keys) == 0 or len(self.col_keys) == 0:
            return ''
        name = tab_name if tab_name is not None else self.name
        if name is not None:
            representation.append(name)

        line = left_upper if left_upper is not None else self.left_upper
        if line is None:
            line = "LeftUpper"

        #sorted_col_keys = self.col_keys if self.col_sorted is None else sorted(self.col_keys, key=self.col_sorted)
        #sorted_row_keys = self.row_keys if self.row_sorted is None else sorted(self.row_keys, key=self.row_sorted)
        sorted_col_keys = sorted(self.col_keys, key=self.col_sorted)
        sorted_row_keys = sorted(self.row_keys, key=self.row_sorted)
        for col_key in sorted_col_keys:
            line += "\t{COL}".format(COL=col_key)
        representation.append(line)

        for row_key in sorted_row_keys:
            line = "{ROW}".format(ROW=row_key)
            for col_key in sorted_col_keys:
                line += "\t{ELEMENT}".format(ELEMENT=self.value(row_key, col_key))
            representation.append(line)

        return '\n'.join(representation)

    def __str__(self):
        return self.name

    def to_nested_list(self):
        """returns the table as a nested list rows"""
        header = [k for k in self.col_keys]
        header.insert(0, " ")
        rows = [header]
        for row_key in self.row_keys:
            row = self.get_row_list(row_key, self.col_keys)
            row.insert(0, row_key)
            rows.append(row)
        return rows

    @staticmethod
    def create_from_json_dict(json_dict):
        ret = Table(name=json_dict['TableName'], left_upper=json_dict['LeftUpper'])
        table_rows = json_dict['Table']
        header = table_rows[0][1:]
        first_col = [row[0] for row in table_rows][1:]
        for r in xrange(len(first_col)):
            row = table_rows[r + 1]
            for c in xrange(len(header)):
                ret.append(first_col[r], header[c], row[c + 1])
        return ret
