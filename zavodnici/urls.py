# coding: utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = patterns(
    '',

    # UPDATEs
    url(r'^editace_zavodnika/(?P<zavodnik_pk>\d+)/$',
        login_required(editace_zavodnika),
        name='editace_zavodnika'),

    url(
        r'^rocnik/(?P<rocnik_pk>\d+)/cislo_autocomplete/$',
        cislo_autocomplete, name='cislo_autocomplete'),

    url(r'^uprav_zavodnika_ze_startovky/(?P<pk>\d+)/$',
        ZavodnikUpdateView.as_view(),
        name='uprav_zavodnika_ze_startovky'),

    url(r'^aktualizuj_data_startovky/(?P<pk>\d+)/$',
        login_required(aktualizuj_data_startovky),
        name='aktualizuj_data_startovky'),

    # DELETE
    url(r'^smaz_zavodnika_ze_startovky/(?P<pk>\d+)/$',
        login_required(smaz_zavodnika_ze_startovky),
        name='smaz_zavodnika_ze_startovky'),
)
