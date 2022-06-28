
from datetime import date

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def desetiny_sekundy(val):
    if val:
        val = str(val).replace('.', ',')
        if ',' not in val:
            val += ',0'
        else:
            ind = val.find(',')
            val = val[:ind + 2]
    else:
        val = ''
    return val


@register.filter
def rozsah_narozeni(roky):
    """ preklada pocatecni rok 0 na text """
    od, do = roky
    if not od:
        return 'nar. {} a starší'.format(do)
    elif date.today().year == do:
        return 'nar. {} a mladší'.format(od)
    else:
        return 'nar. {} - {}'.format(od, do)


@register.simple_tag(takes_context=True)
def th_sortable(context, verbose, order, width=None, kat=0):
    'vrati TH bunku tabulky s pripravenou adresou'
    aktualni_order = context['ordering_str']
    url = reverse('zavody:startovni_listina', args=[context['rocnik'].id])
    # asc_desc + url_smer
    if order in aktualni_order.lstrip('-'):
        # jedna se aktualne razeny sloupec
        if aktualni_order[0] == '-':
            # aktualne je razen sestupne
            caret = 'down'
            url_smer = 'vzestupně'
            url += order
        else:
            # aktualne je razen vzestupne
            caret = 'up'
            url_smer = 'sestupně'
            url += '-' + order
    else:
        # tento sloupec neni nyni razen
        caret = ''
        url_smer = 'vzestupně'
        url += order
    # width
    width = 'width:{0}em'.format(width) if width else ''
    vysledek = """
    <span class='th' style='{1}'>
        <a href='{2}/#kat_{5}' title='seřadit sloupec {3}'>
            <i class='ui caret {0} icon'></i>
            {4}
        </a>
    </span>""".format(
        caret,
        width,
        url,
        url_smer,
        verbose,
        kat)
    return mark_safe(vysledek)


@register.simple_tag(takes_context=True)
def detail_url(context, objekt):
    user = context['user']
    return objekt.get_absolute_url(user)

