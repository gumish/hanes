# coding: utf-8
import csv
from django.utils.text import slugify
from django.core.exceptions import ValidationError


def _clean_radek(i, radek):
    # jednali se o hlavicku nic nevracej
    if not any(radek) or slugify(radek[0]) == 'prijmeni':
        return None
    else:
        try:
            narozen = int(radek[3])
            slug = slugify('-'.join([radek[0], radek[1], radek[3]]))
            return {
                'slug': slug,
                'defaults': {
                    'prijmeni': radek[0],
                    'jmeno': radek[1],
                    'narozen': narozen,
                    'pohlavi': radek[2],
                    },
                'klub': radek[4] or None,
                'cislo': radek[5] or None
                # 'startovni_cas': radek[6] or None,
                # 'cilovy_cas': radek[7] or None
            }
        except:
            return ValidationError(
                u'#{0}: chybějící údaj u člověka: {1[0]},  {1[1]},  {1[2]},  {1[3]}'.format(
                    i,
                    ['???' if not r else r for r in radek]))


def clean_lide_import_csv(soubor):

    def _csv_reader(soubor):
        csv_reader = csv.reader(soubor, delimiter=';')
        for row in csv_reader:
            yield [cell.decode('windows-1250').strip() for cell in row]

    radky = []
    chyby = []
    for i, radek in enumerate(_csv_reader(soubor), start=1):
        data = _clean_radek(i, radek)
        if isinstance(data, ValidationError):
            chyby.append(data)
        elif data:
            radky.append(data)
    return (radky, chyby)
