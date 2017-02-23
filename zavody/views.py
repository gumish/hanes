# coding: utf-8
import json
from io import BytesIO

from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Count
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.text import slugify
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.edit import FormView

from hanes.nested_formsets import nestedformset_factory
from lide.forms import CSVsouborFormular  # , ClovekRocnikForm
from zavodnici.forms import (StarterZavodnikForm, ZavodnikForm,
                             ZavodnikPridaniForm)

from .forms import *
from .functions import (exportuj_kategorie, exportuj_startovku,
                        exportuj_vysledky, rocnik_import)
from .models import Kategorie, Rocnik, Sport, Zavod
from .pdf import PdfPrint
from .templatetags.custom_filters import desetiny_sekundy


# LISTs
def zavody_list_import(request):
    if request.method == 'POST' and request.user.is_staff:
        form = CSVsouborFormular(request.POST, request.FILES)
        if form.is_valid():
            zpravy = rocnik_import(request.FILES['soubor'])
            for zprava in zpravy:
                messages.success(request, zprava)
            return HttpResponseRedirect(reverse('zavody:zavody_list'))
    else:
        form = CSVsouborFormular()

    zavody = Zavod.objects.all()
    return render_to_response(
        'zavody/zavod_list.html',
        {'form': form, 'zavody': zavody},
        context_instance=RequestContext(request))


# DETAILs
class ZavodDetailView(DetailView):
    model = Zavod
    context_object_name = 'zavod'
    template_name = 'zavody/zavod_detail.html'


class RocnikDetailView(DetailView):
    model = Rocnik
    context_object_name = 'rocnik'
    template_name = 'zavody/rocnik_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(RocnikDetailView, self).get_context_data(*args, **kwargs)
        context['kategorie_all'] = self.object.kategorie.annotate(zavodniku=Count('zavodnici_temp'))
        return context


class KategorieDetailView(DetailView):
    model = Kategorie
    context_object_name = 'kategorie'
    template_name = 'zavody/kategorie_detail.html'


# UPDATEs
class ZavodUpdateView(UpdateView):
    model = Zavod
    fields = ['nazev', 'sport', 'korekce_sezony', 'misto', 'info']
    template_name = 'objekt_editace.html'


class RocnikUpdateView(UpdateView):
    model = Rocnik
    fields = ['nazev', 'datum', 'cas', 'misto', 'info']
    template_name = 'objekt_editace.html'


class KategorieUpdateView(UpdateView):
    model = Kategorie
    fields = [
        'nazev',
        'znacka',
        'pohlavi',
        'vek_od',
        'vek_do',
        'atributy',
        'delka_trate',
        'poradi',
        'spusteni_stopek']
    template_name = 'objekt_editace.html'


# DELETEs
class RocnikDeleteView(DeleteView):
    model = Rocnik
    template_name = 'objekt_smazani.html'

    def get_success_url(self):
        return self.object.zavod.get_absolute_url()


class ZavodDeleteView(DeleteView):
    model = Zavod
    template_name = 'objekt_smazani.html'
    success_url = reverse_lazy('zavody:zavody_list')


def vysledkova_listina(request, rocnik_pk):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    kategorie_list = rocnik.kategorie_list()
    # for kat, zavs in kategorie_list:
    #     if kat.id == 57:
    #         for z in zavs:
    #             print z.nedokoncil, type(z.nedokoncil)
    colspan = 1
    if request.method == 'POST':
        sloupce_form = SloupceVysledkoveListinyForm(request.POST)
        if sloupce_form.is_valid():
            colspan = sum(sloupce_form.cleaned_data.values())
    else:
        sloupce_form = SloupceVysledkoveListinyForm()

    return render_to_response(
        'zavody/vysledkova_listina.html', {
            'rocnik': rocnik,
            'kategorie_list': kategorie_list,
            'sloupce_form': sloupce_form,
            'colspan': colspan
        },
        context_instance=RequestContext(request)
    )


# CREATEs
class ZavodPridejView(CreateView):
    form_class = ZavodCreateForm
    template_name = 'zavody/staff/zavod_pridani.html'
    success_url = reverse_lazy('zavody:zavody_list')

    def get_context_data(self, **kwargs):
        context = super(ZavodPridejView, self).get_context_data(**kwargs)
        context.update({'zavody': Zavod.objects.all()})
        return context


class RocnikPridejView(CreateView):
    form_class = RocnikCreateForm
    template_name = 'zavody/staff/rocnik_pridani.html'
    success_url = reverse_lazy('zavody:zavody_list')

    def get_initial(self):
        slug = self.kwargs.get('slug', None)
        self.zavod = Zavod.objects.get(slug=slug)
        return {'zavod': self.zavod}

    def get_context_data(self, **kwargs):
        context = super(RocnikPridejView, self).get_context_data(**kwargs)
        context['posledni_rocnik'] = self.zavod.posledni_rocnik()
        context['zavod'] = self.zavod
        return context

    def form_valid(self, form):
        posledni_rocnik = self.zavod.posledni_rocnik()
        rocnik, kategorie = form.save()
        if not kategorie:
            kategorie = Kategorie.objects.filter(rocnik=posledni_rocnik)
        for kat in kategorie:
            kat.pk = None
            kat.rocnik = rocnik
            kat.save()
        return HttpResponseRedirect(
            rocnik.get_absolute_url())


# FORMs
class ImportZavodnikuView(FormView):
    form_class = ImportZavodnikuCSVForm
    template_name = 'zavody/staff/zavodnici_import_csv.html'

    def get_initial(self):
        pk = self.kwargs.get('pk', None)
        self.rocnik = Rocnik.objects.get(pk=pk)
        return {}

    def get_success_url(self):
        return self.rocnik.get_absolute_url()

    def form_valid(self, form):
        prirazenych, novych = 0, 0
        zavodnici = form.save(self.rocnik)
        for zavodnik, zavodnik_novy, clovek_novy in zavodnici:
            if zavodnik_novy:
                if clovek_novy:
                    novych += 1
                else:
                    prirazenych += 1
        if prirazenych:
            messages.success(
                self.request,
                u'Do ročníku přiřazeno {0} lidí z interního seznamu.'.format(prirazenych))
        if novych:
            messages.success(
                self.request,
                u'Do ročníku přidáno {0} nových lidí,\
                kteří byli i zaregistrování do seznamu lidí.'.format(novych))
        if not any((prirazenych, novych)):
            messages.warning(
                self.request,
                u'Nebylo nic přidáno!')
        return super(ImportZavodnikuView, self).form_valid(form)


def rozkategorizovat_zavodniky(request, rocnik_pk):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    zpravy = rocnik.rozkategorizovat_zavodniky()
    if not zpravy:
        messages.success(request, u'Všichni závodníci zařazení úspěšně do kategorií')
    else:
        for z in zpravy:
            messages.warning(request, z)
    return HttpResponseRedirect(
        reverse('zavody:startovni_listina', args=[rocnik.id]))


def startovni_listina(request, rocnik_pk, ordering_str='vysledny_cas--startovni_cas--cislo'):
    # TODO: vyresit razeni
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    kategorie_list = []
    kategorie_list_temp = rocnik.kategorie_list(ordering_str)
    nezarazeni_temp = rocnik.nezarazeni(ordering_str)

    if request.user.is_active:
        # zarazeni formularu do `kategorie_list`
        for kategorie, zavodnici in kategorie_list_temp:
            formulare = [ZavodnikForm(instance=zav, prefix=zav.id) for zav in zavodnici]
            kategorie_list.append((kategorie, zip(zavodnici, formulare)))

        formulare = [ZavodnikForm(instance=zav, prefix=zav.id) for zav in nezarazeni_temp]
        nezarazeni = zip(nezarazeni_temp, formulare)

        return render_to_response(
            'zavody/staff/startovni_listina.html', {
                'rocnik': rocnik,
                'kategorie_list': kategorie_list,
                'nezarazeni': nezarazeni,
                'ordering_str': ordering_str},
            context_instance=RequestContext(request)
        )
    else:
        return render_to_response(
            'zavody/startovni_listina.html', {
                'rocnik': rocnik,
                'kategorie_list': kategorie_list_temp,
                'nezarazeni': nezarazeni_temp,
                'ordering_str': ordering_str},
            context_instance=RequestContext(request)
        )


def pridani_zavodniku(request, pk):
    """zpracovani formulare `PridaniZavodnikuForm`,
    rozrazeni cloveku do kategorii daneho rocniku zavodu"""

    rocnik = Rocnik.objects.get(pk=pk)
    ZavodnikPridaniFormSet = formset_factory(
        ZavodnikPridaniForm,
        formset=PridaniZavodnikuFormSet,
        extra=20)

    if request.method == 'POST':
        formset = ZavodnikPridaniFormSet(request.POST)

        for f in formset:
            f.instance.rocnik = rocnik
        if formset.is_valid():
            for f in formset:
                f.save()
            formset = ZavodnikPridaniFormSet()
    else:
        formset = ZavodnikPridaniFormSet()
    for f in formset.forms:
        f.fields['kategorie'].queryset = Kategorie.objects.filter(rocnik=rocnik)

    return render_to_response(
        'zavody/staff/zavodnici_pridani.html', {
            'rocnik': rocnik,
            'formset': formset
        },
        context_instance=RequestContext(request)
    )


# def startovni_casy(request, rocnik_pk):
#     "stranka s formsetem zavodniku, jejiz casy budou ovladany javascriptem"
#     rocnik = Rocnik.objects.get(pk=rocnik_pk)
#     return render_to_response(
#         'zavody/staff/startovni_casy.html', {
#             'rocnik': rocnik,
#             'kategorie_list': kategorie_list,
#             'formset': formset
#         },
#         context_instance=RequestContext(request)
#     )


class EditZavodniciView(UpdateView):
    model = Rocnik

    def get_template_names(self):
        return ['zavody/staff/startovni_casy.html']

    def get_form_class(self):
        return nestedformset_factory(
            Rocnik,
            Kategorie,
            inlineformset_factory(
                Kategorie,
                Zavodnik,
                fk_name='kategorie_temp',
                fields=['startovni_cas'],
                can_delete=False,
                extra=0
            ),
            fields=['spusteni_stopek'],
            widgets={
                'spusteni_stopek': forms.TimeInput(
                    attrs={'placeholder': 'hh:mm:ss'}
                )
            },
            can_delete=False,
            extra=0
        )

    def get_success_url(self):
        return '.'  # reverse('blocks-list')


def formular_startera(request, rocnik_pk, ordering_str='startovni_cas--cislo'):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    kategorie_list = []
    queryset = rocnik.zavodnici.filter(kategorie_temp__isnull=False)  # pouze zarazeni do kategorii

    StarterZavodnikFormSet = inlineformset_factory(
        Rocnik, Zavodnik,
        form=StarterZavodnikForm
    )

    if request.method == 'POST':
        formset = StarterZavodnikFormSet(request.POST, instance=rocnik, queryset=queryset)
        if formset.is_valid():
            formset.save()
            messages.success(request, u'Změny úspěšně uloženy')
            return HttpResponseRedirect('.')
        else:
            messages.error(request, u'Chyba ve formuláři! Změny neuloženy..')
    else:
        formset = StarterZavodnikFormSet(instance=rocnik, queryset=queryset)

    # formulare formsetu do tvaru slovniku, pro jejich individualni volani
    formulare_dict = {
        f.instance.id: f for f in formset.forms if f.instance
    }

    # zarazeni formularu do `kategorie_list`
    for kategorie, zavodnici in rocnik.kategorie_list(ordering_str):
        formulare = [formulare_dict[zav.id] for zav in zavodnici if zav.id in formulare_dict]
        kategorie_list.append((kategorie, zip(zavodnici, formulare)))

    return render_to_response(
        'zavody/staff/formular_startera.html', {
            'rocnik': rocnik,
            'kategorie_list': kategorie_list,
            'formset': formset
        },
        context_instance=RequestContext(request)
    )


def cilovy_formular(request, rocnik_pk):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    CilovyFormularFormSet = formset_factory(
        CilovyFormular,
        formset=KontrolaCiselFormSet,
        extra=20)

    if request.method == 'POST':
        formset = CilovyFormularFormSet(request.POST)
        for f in formset.forms:
            f.rocnik = rocnik
        if formset.is_valid():
            for f in formset.forms:
                f.save()
            formset = CilovyFormularFormSet()
    else:
        formset = CilovyFormularFormSet()

    return render_to_response(
        'zavody/staff/cilovy_formular.html', {
            'rocnik': rocnik,
            'formset': formset
        },
        context_instance=RequestContext(request)
    )


def startovka_export(request, rocnik_pk, ordering_str='cislo'):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    filename = '{0}__{1}__startovka'.format(slugify(rocnik.zavod), rocnik.datum.year)
    response = HttpResponse(content_type='text/csv', charset='cp1250')
    response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(filename)
    response = exportuj_startovku(response, rocnik, ordering_str)
    return response


def vysledky_export(request, rocnik_pk):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    filename = '{0}__{1}__vysledky'.format(slugify(rocnik.zavod), rocnik.datum.year)
    response = HttpResponse(content_type='text/csv', charset='cp1250')
    response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(filename)
    response = exportuj_vysledky(response, rocnik)
    return response


def kategorie_export(request, rocnik_pk):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    filename = '{0}__{1}__kategorie'.format(slugify(rocnik.zavod), rocnik.datum.year)
    response = HttpResponse(content_type='text/csv', charset='cp1250')
    response['Content-Disposition'] = 'attachment; filename={0}.csv'.format(filename)
    response = exportuj_kategorie(response, rocnik)
    return response


def sport_autocomplete(request):
    vysledek = []
    if 'query' in request.GET:
        query = slugify(request.GET['query'].encode('utf8'))
        sporty = Sport.objects.filter(slug__contains=query).values_list('nazev', flat=True)
        for sport in sporty:
            vysledek.append({'value': sport})
    return HttpResponse(
        json.dumps({'suggestions': vysledek}),
        content_type='application/json')


def zavod_autocomplete(request):
    vysledek = []
    if 'query' in request.GET:
        query = slugify(request.GET['query'].encode('utf8'))
        zavody = Zavod.objects.filter(slug__contains=query)
        for zavod in zavody:
            vysledek.append({
                'value': zavod.nazev, 'sport': zavod.sport.nazev
            })
    return HttpResponse(
        json.dumps({'suggestions': vysledek}),
        content_type='application/json')

TITLE_TEMPLATE = u'{0.znacka} - {0.nazev} &nbsp;&nbsp; nar. {1[0]}-{1[1]} &nbsp;&nbsp; trať: {0.delka_trate}'


def vysledky_kategorie_PDF(request, kategorie_pk):
    kategorie = Kategorie.objects.get(pk=kategorie_pk)
    rows = []
    widths = [1.2, 1.2, 3, 2.5, 1.5, 5, 2.3, 2.3, 1.5]
    for zavodnik in kategorie.serazeni_zavodnici(razeni=None):
        rows.append([
            zavodnik.poradi_v_kategorii() or '',
            zavodnik.cislo or '',
            zavodnik.clovek.prijmeni,
            zavodnik.clovek.jmeno,
            zavodnik.clovek.narozen,
            zavodnik.klub.nazev if zavodnik.klub else '',
            zavodnik.nedokoncil or desetiny_sekundy(zavodnik.vysledny_cas),
            desetiny_sekundy(zavodnik.casova_ztrata) or '',
            zavodnik.poradi_na_trati() or ''
        ])
    pdf_print = PdfPrint(BytesIO())
    right_aligned = [0, 1, 8]
    pdf = pdf_print.sheet(
        [{
            'title': TITLE_TEMPLATE.format(kategorie, kategorie.rozsah_narozeni()),
            'headers': ([
                u'poř.', u'číslo', u'příjmení', u'jméno', u'nar.', u'klub',
                u'výsledný čas', u'časová ztráta', u'na trati'],),
            'rows': rows}],
        widths, right_aligned)
    return HttpResponse(pdf, content_type='application/pdf')


def vysledky_rocnik_PDF(request, rocnik_pk):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    pdf_print = PdfPrint(BytesIO())
    tables = []
    for kategorie in rocnik.kategorie.all():
        rows = []
        for zavodnik in kategorie.serazeni_zavodnici(razeni=None):
            rows.append([
                zavodnik.poradi_v_kategorii() or '',
                zavodnik.cislo or '',
                zavodnik.clovek.prijmeni,
                zavodnik.clovek.jmeno,
                zavodnik.clovek.narozen,
                zavodnik.klub.nazev if zavodnik.klub else '',
                zavodnik.nedokoncil or desetiny_sekundy(zavodnik.vysledny_cas),
                desetiny_sekundy(zavodnik.casova_ztrata) or '',
                zavodnik.poradi_na_trati() or ''
                ])
        tables.append({
            'title': TITLE_TEMPLATE.format(kategorie, kategorie.rozsah_narozeni()),
            'headers': ([
                u'poř.', u'číslo', u'příjmení', u'jméno', u'nar.', u'klub',
                u'výsledný čas', u'časová ztráta', u'na trati'],),
            'rows': rows})

    widths = [1.2, 1.2, 3, 2.5, 1.5, 5, 2.3, 2.3, 1.5]
    right_aligned = [0, 1, 8]
    pdf = pdf_print.sheet(tables, widths, right_aligned)
    return HttpResponse(pdf, content_type='application/pdf')

def startovka_kategorie_PDF(request, kategorie_pk):
    kategorie = Kategorie.objects.get(pk=kategorie_pk)
    rows = []
    widths = [1.5, 3, 2.7, 1.5, 6, 3]
    for zavodnik in kategorie.serazeni_zavodnici(razeni=None):
        rows.append([
                zavodnik.cislo or '',
                zavodnik.clovek.prijmeni,
                zavodnik.clovek.jmeno,
                zavodnik.clovek.narozen,
                zavodnik.klub.nazev if zavodnik.klub else '',
                zavodnik.nedokoncil or desetiny_sekundy(zavodnik.startovni_cas),
            ])
    pdf_print = PdfPrint(BytesIO())
    pdf = pdf_print.sheet(
        [{
            'title': TITLE_TEMPLATE.format(kategorie, kategorie.rozsah_narozeni()),
            'headers': ([u'číslo', u'příjmení', u'jméno', u'nar.', u'klub', u'startovní čas'],),
            'rows': rows}],
        widths)
    return HttpResponse(pdf, content_type='application/pdf')


def startovka_rocnik_PDF(request, rocnik_pk):
    rocnik = Rocnik.objects.get(pk=rocnik_pk)
    pdf_print = PdfPrint(BytesIO())
    tables = []
    for kategorie in rocnik.kategorie.all():
        rows = []
        widths = [1.5, 3, 2.7, 1.5, 6, 3]
        for zavodnik in kategorie.serazeni_zavodnici(razeni='startovni_cas--cislo'):
            rows.append([
                    zavodnik.cislo or '',
                    zavodnik.clovek.prijmeni,
                    zavodnik.clovek.jmeno,
                    zavodnik.clovek.narozen,
                    zavodnik.klub.nazev if zavodnik.klub else '',
                    zavodnik.nedokoncil or desetiny_sekundy(zavodnik.startovni_cas),
                ])
        tables.append({
            'title': TITLE_TEMPLATE.format(kategorie, kategorie.rozsah_narozeni()),
            'headers': ([u'číslo', u'příjmení', u'jméno', u'nar.', u'klub', u'startovní čas'],),
            'rows': rows})

    pdf = pdf_print.sheet(tables, widths)
    return HttpResponse(pdf, content_type='application/pdf')
