import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.forms.forms import pretty_name

from revo.common.excel_report_base import ExcelReportBase


def get_column_head(model, name):
    names = name.split(".")
    tmp = ''

    for i in names:
        tmp += model._meta.get_field(i).verbose_name
        tmp += '.'
    tmp = tmp[:-1]
    return pretty_name(tmp)


class QuerySetToExcel(ExcelReportBase):
    def __init__(self, filename, queryset, columns):
        super().__init__()
        self.row = 0
        self.col = 0
        self.setup(filename)
        self.book.remove_timezone = True
        self.sheet = self.book.add_worksheet()
        self.columns = columns  # [('field', 'width','format')]
        self.queryset = queryset
        self.set_column_widths()
        self.write_heading()
        self.write_data()

    def output(self):
        self.book.close()

    def set_column_widths(self):
        width_list = [x[1] for x in self.columns]
        for i, width in enumerate(width_list):
            self.sheet.set_column(i, i, width)

    def write_heading(self):
        for num, column in enumerate(self.columns):
            if len(column) > 3:
                value = column[3]
            else:
                value = get_column_head(self.queryset.model, column[0])
            self.sheet.write_string(self.row, self.col, value, self.col_header)
            self.col += 1

    def write_data(self):  # match line item with sql item
        self.row += 1
        self.col = 0
        for line in self.queryset:
            for num, column in enumerate(self.columns):
                field_name = column[0]
                # if len(column) > 2:
                #
                # else:
                xl_format = self.get_column_format(self.queryset.model, field_name)
                self.sheet.write(self.row, self.col, getattr(line, field_name), xl_format)
                self.col += 1
            self.row += 1
            self.col = 0

    def get_column_format(self, model, name):
        ftype = model._meta.get_field(name).get_internal_type()
        if ftype in ('DateField', 'DateTimeField'):
            return self.date_format
        if ftype in ('FloatField',):
            return self.number_format
        if ftype in ('DecimalField',):
            num_decimals = model._meta.get_field(name).decimal_places
            return self.decimal_format2
        return self.defaultformat
