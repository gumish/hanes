
import csv
from io import TextIOWrapper
from django.utils.text import slugify
from django.core.exceptions import ValidationError


def zavodnici_import_clean_csv(soubor) -> tuple[list, list]:
    """ startovni_cislo
        prijmeni *
        jmeno *
        narozen * [rok]
        pohlavi * [m/z]
        klub_nazev
        klub_zkratka
        klub_id
        vysledny_cas
        kategorie_nazev
        kategorie_vek_od
        kategorie_vek_do_vcetne
        kategorie_delka_trate
        kategorie_znacka
    """

    def _csv_reader(soubor):
        """ prevede csv soubor, ktery muze byt ve formatu:
            - windows-1250 (cp1250)
            - utf-8
            vraci list radku, kde kazdy radek je list
        """
        encodings = ['windows-1250', 'utf-8']
        for encoding in encodings:
            try:
                soubor.seek(0)
                soubor_text = TextIOWrapper(soubor, encoding=encoding)
                csv_reader = csv.reader(soubor_text, delimiter=';')
                for row in csv_reader:
                    yield [cell.strip() for cell in row]
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Nepodařilo se dekódovat soubor. Podporované kódování: " + ", ".join(encodings))


    def _clean_radek(i, hlavicka, radek) -> dict | ValidationError | None:

        # namapovani dat do slovniku
        data = {}
        for index, promenna in enumerate(hlavicka):
            if index < len(radek):
                data[promenna] = radek[index]
            else:
                data[promenna] = None

        try:
            return {
                'slug': slugify(f'{data["prijmeni"]}-{data["jmeno"]}-{data["narozen"]}'),
                'defaults': {
                    'prijmeni': data.pop('prijmeni'),
                    'jmeno': data.pop('jmeno'),
                    'narozen': int(data.pop('narozen')),
                    'pohlavi': data['pohlavi']
                },
                **data
            }
        except Exception as e:
            return ValidationError(
                '#{0}: chybějící údaj u člověka: {1}'.format(
                    i,
                    ', '.join(['???' if not r else r for r in radek])))

    radky = []
    chyby = []
    for i, radek in enumerate(_csv_reader(soubor), start=1):

        if i == 1:  # hlavicka, prvni radek
            hlavicka = [r.split(maxsplit=1)[0] for r in radek] # odstraneni vseho za mezerou
            continue

        data = _clean_radek(i, hlavicka, radek)

        if isinstance(data, ValidationError):
            chyby.append(data)
        elif data:
            radky.append(data)
    return (radky, chyby)


def cistit_clenstvi():
    """ utilita pro odstraneni duplicitnich clenstvi
        nepouzite ve webu, pouze pro shell konzoli
    """
    from lide.models import Clenstvi
    smazat = []
    for c in Clenstvi.objects.all():
        try:
            c.full_clean()
        except Exception as e:
            ds = Clenstvi.objects.filter(clovek=c.clovek, klub=c.klub, sport=c.sport).order_by('-priorita')
            smazat.extend([d.id for d in ds[1:]])
    if smazat:
        print(smazat)
        Clenstvi.objects.filter(id__in=smazat).delete()
