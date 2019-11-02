
import json
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.template.loader import render_to_string

from .models import Zavodnik
from .forms import *
from zavody.templatetags.custom_filters import desetiny_sekundy
from lide.views import _referer_do_session

# FORMs
def editace_zavodnika(request, zavodnik_pk):
    zavodnik = Zavodnik.objects.get(pk=zavodnik_pk)
    rocnik = zavodnik.rocnik
    if request.method == 'POST':
        form = ZavodnikEditaceForm(request.POST, instance=zavodnik)
        # TODO validace cisla pri zmene cloveka!
        if form.is_valid():
            form.save()
            # return HttpResponseRedirect(
            #     '{0}#zavodnik_{1}'.format(
            #         reverse('zavody:startovni_listina', args=[rocnik.id]),
            #         zavodnik.id))
            return HttpResponseRedirect(request.session['referer'])
    else:
        _referer_do_session(request)
        form = ZavodnikEditaceForm(instance=zavodnik)
    return render(request,
        'zavody/staff/zavodnik_editace.html', {
            'zavodnik': zavodnik,
            'rocnik': rocnik,
            'form': form
        },
        
    )


def cislo_autocomplete(request, rocnik_pk=None):
    vysledek = []
    for z in Zavodnik.objects.filter(cislo=request.GET['query'], rocnik__pk=rocnik_pk):
        vysledek.append({
            'value': str(z.cislo),
            'data': {
                'jmeno': z.clovek.cele_jmeno(),
                'cas': str(z.cilovy_cas) if z.cilovy_cas else None,
                'nedokoncil': z.nedokoncil
            }
        })
    return HttpResponse(
        json.dumps({'suggestions': vysledek}),
        content_type='application/json')


# AJAX

def _desetiny_sekundy(puvodni_dict):
    """funkce jez projede slovnik a upravi casy"""
    for k, v in list(puvodni_dict.items()):
        if k.endswith('_cas') and v:
            puvodni_dict[k] = desetiny_sekundy(str(v))
    return puvodni_dict


class ZavodnikUpdateView(UpdateView):
    "startovni listina: zmena zavodnika pomoci ajaxu"
    form_class = ZavodnikForm
    model = Zavodnik

    def get_form_kwargs(self):
        kwargs = super(ZavodnikUpdateView, self).get_form_kwargs()
        kwargs.update({'prefix': self.kwargs['pk']})
        return kwargs

    def form_invalid(self, form):
        response = super(ZavodnikUpdateView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        if self.request.is_ajax():
            zavodnik = form.save()
            html = render_to_string(
                'zavody/staff/_startovka_zavodnik_form.html',
                {
                    'zavodnik': zavodnik,
                    'formular': ZavodnikForm(instance=zavodnik, prefix=zavodnik.id)},
                request=self.request
            )
            return HttpResponse(html)
        else:
            return super(ZavodnikUpdateView, self).form_valid(form)


def smaz_zavodnika_ze_startovky(request, pk):
    "startovni listina: smazani zavodnika pomoci ajaxu"
    try:
        Zavodnik.objects.get(pk=pk).delete()
        return HttpResponse(True)
    except Exception as e:
        print(e)
        return HttpResponse(e, status=500)


def aktualizuj_data_startovky(request, pk):
    "startovni listina: aktualizace zavodnika pomoci ajaxu"
    zavodnik = Zavodnik.objects.get(pk=pk)
    html = render_to_string(
        'zavody/staff/_startovka_zavodnik_form.html',
        {
            'zavodnik': zavodnik,
            'formular': ZavodnikForm(instance=zavodnik, prefix=zavodnik.id)},
        request=request
    )
    return HttpResponse(html)
