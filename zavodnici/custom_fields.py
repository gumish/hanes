
from django import forms
from zavody.templatetags.custom_filters import desetiny_sekundy


def _format_hanes_time(value):
    value = str(float(value.replace(',', '.')))  # jde o cislo?
    hms, us = value.split('.')
    s = hms[-2:] or '00'
    m = hms[-4:-2] or '00'
    h = hms[-6:-4] or '00'
    return '{}:{}:{},{}'.format(h, m, s, us)


# CUSTOM WIDGET
# -------------
class CustomTimeInput(forms.TimeInput):
    'Trida pro zaokrouhleni mikrosekund puvodniho `TimeInput` na destiny sekund'
    supports_microseconds = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = '%H:%M:%S,%f'

    def format_value(self, value):
        value = super().format_value(value)
        value = desetiny_sekundy(value)
        return value


# CUSTOM FIELD
# ------------
class CustomTimeField(forms.TimeField):
    'Trida pro zahrunuti zlomku sekundy do puvodniho `TimeField`'
    TIME_INPUT_FORMATS = (
        '%H:%M:%S,%f',
        '%H-%M-%S,%f',
        '%M:%S,%f',
        '%M-%S,%f',
        '%H:%M:%S.%f',
        '%H-%M-%S.%f',
        '%M:%S.%f',
        '%M-%S.%f',
        '%H:%M:%S',
        '%H-%M-%S',
        '%M:%S',
        '%M-%S')

    def __init__(self, *args, **kwargs):
        super(CustomTimeField, self).__init__(*args, **kwargs)
        self.input_formats = self.TIME_INPUT_FORMATS
        self.required = False
        self.widget = CustomTimeInput()

    def to_python(self, value):
        '''nejprve se pokusi utvorit z retezce-cisla retezec
        v podporovanem formatu,pak to preda klasickemu postupu TimeField'''
        try:
            value = _format_hanes_time(value)
        except:
            pass
        return super(CustomTimeField, self).to_python(value)
