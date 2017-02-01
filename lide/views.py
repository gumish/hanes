# coding: utf-8
import json
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Count
from django.forms.models import inlineformset_factory
from django.utils.text import slugify


from .models import Clovek, Clenstvi
from .forms import ClovekUpdateForm, LideImportCSVForm
from zavody.models import Rocnik


def _referer_do_session(request):
    referer = request.META.get('HTTP_REFERER', '')
    if not referer.endswith(request.path):
        request.session['referer'] = referer


# DETAILs
class ClovekDetailView(DetailView):
    model = Clovek
    context_object_name = 'clovek'
    template_name = 'lide/clovek_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ClovekDetailView, self).get_context_data(**kwargs)
        context['zavodnici'] = self.object.zavodnici.filter(kategorie_temp__isnull=False).order_by('-rocnik__datum')
        context['jmenovci'] = Clovek.objects.filter(
            prijmeni__istartswith=self.object.prijmeni.rstrip(u'ová')).exclude(pk=self.object.pk)
        _referer_do_session(self.request)
        context['referer'] = self.request.session.get('referer', None)
        return context


class LideImportCSV(FormView):
    form_class = LideImportCSVForm
    template_name = 'lide/staff/lide_import_csv.html'
    success_url = reverse_lazy('lide:lide_list')

    def form_valid(self, form):
        lide = form.save()
        novy_lide, nove_kluby = 0, 0
        for radek in lide:
            if radek[2]:
                novy_lide += 1
            if radek[3]:
                nove_kluby += 1
        if novy_lide:
            messages.success(
                self.request,
                u'Přidáno {0} lidí do seznamu.'.format(novy_lide))
        if nove_kluby:
            messages.success(
                self.request,
                u'Přidáno {0} klubů do seznamu.'.format(nove_kluby))
        if not any((novy_lide, nove_kluby)):
            messages.warning(
                self.request,
                u'Nebylo nic přidáno!')
        return super(LideImportCSV, self).form_valid(form)


def clovek_update(request, slug):
    clovek = Clovek.objects.get(slug=slug)
    zavodnici = clovek.zavodnici.filter(kategorie_temp__isnull=False).order_by('-rocnik__datum')
    jmenovci = Clovek.objects.filter(
            prijmeni__istartswith=clovek.prijmeni.rstrip(u'ová')).exclude(slug=clovek.slug)
    ClenstviFormSet = inlineformset_factory(
        Clovek,
        Clenstvi,
        extra=1,
        fields=('klub', 'sport', 'priorita'))
    if request.method == 'POST':
        form = ClovekUpdateForm(request.POST, instance=clovek)
        clenstvi_formset = ClenstviFormSet(request.POST, instance=clovek)
        if form.is_valid() and clenstvi_formset.is_valid():
            clovek, zpravy = form.save()  # clovek se zde muze zmenit
            for zprava in zpravy:
                messages.success(request, zprava)
            if clovek:
                clenstvi_formset.instance = clovek
                clenstvi_formset.save()
                return HttpResponseRedirect(clovek.get_absolute_url(request.user))
            else:
                # pokud byl klub smazan a nebyl urcen novy klub clenum, pak presmeruj na seznam klubu
                return HttpResponseRedirect(reverse('lide:lide_list'))
    else:
        _referer_do_session(request)
        form = ClovekUpdateForm(instance=clovek)
        clenstvi_formset = ClenstviFormSet(instance=clovek)
    return render_to_response(
        'lide/staff/clovek_editace.html', {
            'clovek': clovek,
            'zavodnici': zavodnici,
            'jmenovci': jmenovci,
            'form': form,
            'clenstvi_formset': clenstvi_formset,
            'referer': request.session.get('referer', None)},
        context_instance=RequestContext(request))


def clovek_list(request):
    lide = Clovek.objects.all().annotate(
        pocet_zavodu=Count('zavodnici'))
    for clovek in lide:
        clovek.kluby = clovek.clenstvi.values_list('klub', flat=True).distinct()
    return render_to_response(
        'lide/clovek_list.html',
        {'lide': lide},
        context_instance=RequestContext(request))


def clovek_autocomplete(request, rocnik_pk=None):
    vysledek = []
    if rocnik_pk:
        rocnik = Rocnik.objects.get(pk=rocnik_pk)
    if 'query' in request.GET:
        # query rozdeli na dle mezery na prijmeni a jmeno
        query = slugify(request.GET['query'].encode('utf8')).split('-')
        lide = Clovek.objects.filter(prijmeni_slug__startswith=query[0])
        if len(query) > 1:
            lide = lide.filter(jmeno_slug__startswith=query[1])

        for clovek in lide:
            zavodnik_oznac = ''
            if rocnik:
                serazene_clenstvi = clovek.serazene_clenstvi_pro_zavod(rocnik.zavod)
                zavodnik = rocnik.zavodnici.filter(clovek=clovek).first()
                if zavodnik:
                    zavodnik_oznac = zavodnik.cislo or '???'
            else:
                serazene_clenstvi = None
            vysledek.append({
                'value': clovek.prijmeni,
                'data': {
                    'prijmeni': clovek.prijmeni,
                    'jmeno': clovek.jmeno,
                    'pohlavi': clovek.pohlavi,
                    'narozen': clovek.narozen,
                    'klub': serazene_clenstvi[0].klub.nazev if serazene_clenstvi else '',
                    'zavodnik': zavodnik_oznac,
                    'clovek_id': clovek.id
                }
            })
        # seradit dle klubu, kvuli groupovani v napovede
        vysledek.sort(key=lambda i: (i['data']['klub'], i['value']))
    return HttpResponse(
        json.dumps({'suggestions': vysledek}),
        content_type='application/json')


# UTILITY
def duplicity(request):
    seen = set()
    duplicity = set()
    for clovek in Clovek.objects.all():
        x = clovek.prijmeni_slug + '-' + clovek.jmeno_slug
        if x not in seen:
            seen.add(x)
        else:
            duplicity.add(clovek)
    return HttpResponse('<br>'.join([str(x) for x in duplicity]))
