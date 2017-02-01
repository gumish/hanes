# coding: utf-8
import json
from django.views.generic import DetailView, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Count
from django.utils.text import slugify


from .models import Klub
from lide.models import Clovek
from .forms import KlubUpdateForm
from lide.views import _referer_do_session


class KlubyListView(ListView):
    context_object_name = 'kluby'
    queryset = Klub.objects.annotate(pocet_clenstvi=Count('clenstvi'))
    template_name = 'lide/klub_list.html'


# DETAILs
class KlubDetailView(DetailView):
    model = Klub
    context_object_name = 'klub'
    template_name = 'lide/klub_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KlubDetailView, self).get_context_data(**kwargs)
        _referer_do_session(self.request)
        context['referer'] = self.request.session.get('referer', None)
        clenove = []
        for clen in self.object.clenstvi.all():
            if clen.clovek not in clenove:
                clenove.append(clen.clovek)
        context['clenove'] = clenove
        return context


class KlubUpdateView(UpdateView):
    form_class = KlubUpdateForm
    model = Klub
    context_object_name = 'klub'
    template_name = 'lide/staff/klub_editace.html'

    def get_context_data(self, **kwargs):
        context = super(KlubUpdateView, self).get_context_data(**kwargs)
        _referer_do_session(self.request)
        context['referer'] = self.request.session.get('referer', None)
        clenove = []
        for clen in self.object.clenstvi.all():
            if clen.clovek not in clenove:
                clenove.append(clen.clovek)
        context['clenove'] = clenove
        return context

    def form_valid(self, form):
        klub, zpravy = form.save()
        for zprava in zpravy:
            messages.success(self.request, zprava)
        if klub:
            return HttpResponseRedirect(klub.get_absolute_url(self.request.user))
        else:
            # pokud byl klub smazan a nebyl urcen novy klub clenum, pak presmeruj na seznam klubu
            return HttpResponseRedirect(reverse('kluby:kluby_list'))


def klub_autocomplete(request):
    vysledek = []

    if 'query' in request.GET:
        query = slugify(request.GET['query'].encode('utf8'))
        kluby = Klub.objects.filter(slug__contains=query)

    if 'clovek_id' in request.GET:
        clovek = Clovek.objects.get(pk=request.GET['clovek_id'])
        vlastni_kluby = Klub.objects.filter(clenstvi__clovek=clovek).order_by('-clenstvi__sport', '-clenstvi__priorita')
        kluby = kluby.exclude(clenstvi__clovek=clovek)
    else:
        vlastni_kluby = []
    for kluby, skupina in ((vlastni_kluby, u'registrované'), (kluby, u'ostatní')):
        pouzite_kluby = []
        for klub in kluby:
            if klub not in pouzite_kluby:
                vysledek.append({
                    'value': klub.nazev,
                    'data': {
                        'skupina': skupina,
                    }
                })
                pouzite_kluby.append(klub)

    return HttpResponse(
        json.dumps({'suggestions': vysledek}),
        content_type='application/json')
