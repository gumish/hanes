from django.http import HttpResponse
from django.template import context
from django.views.generic import DetailView, ListView
from io import BytesIO
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, NamedFormsetsMixin

from zavody.pdf import PdfPrint
from zavody.views import TITLE_TEMPLATE
from zavodnici.views import desetiny_sekundy

from .forms import PoharCreateForm, PocetZavoduPoharuSportuInline
from .models import KategoriePoharu, Pohar


# Class Based Views
# -----------------

class PoharyListView(ListView):
    model = Pohar
    template_name = "pohary/pohar_list.html"


class PoharDetailView(DetailView):
    model = Pohar
    template_name = "pohary/pohar_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pohar = self.object
        zavodnici = pohar.zavodnici_vsichni()
        context["rocniky"] = []
        context["kluby"] = []

        for rocnik in pohar.rocniky.all():
            zavodniku = zavodnici.filter(rocnik=rocnik).count()
            context["rocniky"].append((rocnik, zavodniku))

        for klub in pohar.kluby.all():
            zavodniku = zavodnici.filter(klub=klub).count()
            context["kluby"].append((klub, zavodniku))

        return context


class KategoriePoharuDetailView(DetailView):
    model = KategoriePoharu
    context_object_name = "kategorie"
    template_name = "pohary/kategoriepoharu_detail.html"

    def get_context_data(self, **kwargs):
        context = super(KategoriePoharuDetailView, self).get_context_data(**kwargs)
        context["pohar"] = self.object.pohar
        return context


class PoharCreateUpdateMixin(NamedFormsetsMixin):
    model = Pohar
    form_class = PoharCreateForm
    inlines_names = ["pocet_zavodu_poharu_sportu"]
    inlines = [PocetZavoduPoharuSportuInline]
    template_name = "pohary/pohar_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pohary"] = Pohar.objects.all()
        return context

    def form_valid(self, form):
        """Nakopirovani hodnot kategorii z prvniho zavodu"""
        response = super().form_valid(form)
        pohar = self.object
        notcopy_values = ["id", "delka_trate", "rocnik_id", "spusteni_stopek", "startovne"]
        if form.cleaned_data["kopirovat_kategorie"]:
            rocnik = pohar.rocniky.first()
            kategorie_values = rocnik.kategorie.all().values()
            for values in kategorie_values:
                values = {key: value for key, value in values.items() if key not in notcopy_values}
                values["pohar"] = pohar
                KategoriePoharu.objects.create(**values)
        return response


class PoharCreateView(PoharCreateUpdateMixin, CreateWithInlinesView):
    pass


class PoharUpdateView(PoharCreateUpdateMixin, UpdateWithInlinesView):
    pass



# Function Based Views
# --------------------

def vysledky_kategorie_pdf(request, kategorie_pk):
    """Zobtazi vysledky kategorie do PDF, vrati HttpResponse s PDF souborem"""

    from zavody.templatetags import custom_filters

    kategorie = KategoriePoharu.objects.get(pk=kategorie_pk)
    rows = []
    widths = [1.5, 1.5, 3, 2.7, 1.5, 6, 2.3, 1.5]
    for zavodnik in kategorie.poradi_zavodniku():
        rows.append(
            [
                zavodnik.poradi_v_kategorii() or "",
                zavodnik.cislo or "",
                zavodnik.clovek.prijmeni,
                zavodnik.clovek.jmeno,
                zavodnik.clovek.narozen,
                zavodnik.klub.nazev if zavodnik.klub else "",
                zavodnik.nedokoncil or desetiny_sekundy(zavodnik.vysledny_cas),
                zavodnik.poradi_na_trati() or "",
            ]
        )
    pdf_print = PdfPrint(BytesIO())
    pdf = pdf_print.sheet(
        [
            {
                "title": TITLE_TEMPLATE.format(
                    kategorie,
                    custom_filters.rozsah_narozeni(kategorie.rozsah_narozeni()),
                ),
                "headers": (
                    [
                        "pořadí",
                        "číslo",
                        "příjmení",
                        "jméno",
                        "nar.",
                        "klub",
                        "výsledný čas",
                        "na trati",
                    ],
                ),
                "rows": rows,
            }
        ],
        widths,
    )
    return HttpResponse(pdf, content_type="application/pdf")
