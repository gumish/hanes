# coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from django.http import HttpResponseRedirect

from .models import KategoriePoharu, Pohar
from .forms import PoharCreateForm


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
            for values in rocnik.kategorie.all().values():
                del values['id']
                del values['delka_trate']
                del values['rocnik_id']
                del values['spusteni_stopek']
                values['pohar'] = pohar
                KategoriePoharu.objects.create(**values)
        return HttpResponseRedirect(
            pohar.get_absolute_url())
