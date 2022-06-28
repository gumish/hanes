
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import CreateView, DetailView, ListView
from io import BytesIO

from zavody.pdf import PdfPrint
from zavody.views import TITLE_TEMPLATE
from zavodnici.views import desetiny_sekundy

from .forms import PoharCreateForm
from .models import KategoriePoharu, Pohar


class PoharyListView(ListView):
    model = Pohar
    template_name = 'pohary/pohar_list.html'


class PoharDetailView(DetailView):
    model = Pohar
    template_name = 'pohary/pohar_detail.html'


class KategoriePoharuDetailView(DetailView):
    model = KategoriePoharu
    context_object_name = 'kategorie'
    template_name = 'pohary/kategoriepoharu_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KategoriePoharuDetailView, self).get_context_data(**kwargs)
        context['pohar'] = self.object.pohar
        return context


class PoharCreateView(CreateView):
    form_class = PoharCreateForm
    template_name = 'pohary/pohar_create.html'
    success_url = reverse_lazy('pohary:pohary_list')

    def get_context_data(self, **kwargs):
        context = super(PoharCreateView, self).get_context_data(**kwargs)
        context['pohary'] = Pohar.objects.all()
        return context

    def form_valid(self, form):
        "nakopirovani hodnot kategorii z prvniho zavodu"
        pohar = form.save()
        if form.cleaned_data['kopirovat_kategorie']:
            rocnik = pohar.rocniky.first()
            for values in list(rocnik.kategorie.all().values()):
                del values['id']
                del values['delka_trate']
                del values['rocnik_id']
                del values['spusteni_stopek']
                del values['startovne']
                values['pohar'] = pohar
                KategoriePoharu.objects.create(**values)
        return HttpResponseRedirect(
            pohar.get_absolute_url())


def vysledky_kategorie_pdf(request, kategorie_pk):

    from zavody.templatetags import custom_filters

    kategorie = KategoriePoharu.objects.get(pk=kategorie_pk)
    rows = []
    widths = [1.5, 1.5, 3, 2.7, 1.5, 6, 2.3, 1.5]
    for zavodnik in kategorie.serazeni_zavodnici(razeni=None):
        rows.append([
                zavodnik.poradi_v_kategorii() or '',
                zavodnik.cislo or '',
                zavodnik.clovek.prijmeni,
                zavodnik.clovek.jmeno,
                zavodnik.clovek.narozen,
                zavodnik.klub.nazev if zavodnik.klub else '',
                zavodnik.nedokoncil or desetiny_sekundy(zavodnik.vysledny_cas),
                zavodnik.poradi_na_trati() or ''
            ])
    pdf_print = PdfPrint(BytesIO())
    pdf = pdf_print.sheet(
        [{
            'title': TITLE_TEMPLATE.format(
                kategorie, 
                custom_filters.rozsah_narozeni(kategorie.rozsah_narozeni())
            ),
            'headers': (['pořadí', 'číslo', 'příjmení', 'jméno', 'nar.', 'klub', 'výsledný čas', 'na trati'],),
            'rows': rows}],
        widths)
    return HttpResponse(pdf, content_type='application/pdf')
