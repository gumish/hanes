# coding: utf-8

from django.conf.urls import patterns, url
# from django.contrib.auth.decorators import login_required

from .views import PoharyListView, PoharDetailView, KategoriePoharuDetailView, PoharCreateView

urlpatterns = patterns(
    '',
    # LISTs
    url(r'^$',
        PoharyListView.as_view(),
        name='pohary_list'),

    # DETAILs
    url(r'^detail/(?P<slug>[-\w]+)/$',
        PoharDetailView.as_view(),
        name='pohar_detail'),
    url(r'^kategorie/(?P<pk>\d+)/$',
        KategoriePoharuDetailView.as_view(),
        name='kategorie-poharu_detail'),
    url(r'^pridat/$',
        PoharCreateView.as_view(),
        name='pohar_create'),
)
