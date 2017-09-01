# coding: utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import *

urlpatterns = patterns(
    '',
    # LISTs
    url(r'^$',
        ZavodyListView.as_view(),
        name='zavody_list'),

    # DETAILs
    url(r'^detail/(?P<pk>\d+)/$',
        ZavodDetailView.as_view(),
        name='zavod_detail'),
    url(r'^rocnik/(?P<pk>\d+)/detail/$',
        RocnikDetailView.as_view(),
        name='rocnik_detail'),
    url(r'^kategorie/(?P<pk>\d+)/$',
        KategorieDetailView.as_view(),
        name='kategorie_detail'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/vysledkova_listina/$',
        vysledkova_listina,
        name='vysledkova_listina'),

    # CREATEs
    url(r'^zavod/novy/$',
        ZavodPridejView.as_view(),
        name='zavod_pridani'),
    url(r'^(?P<slug>[-\w]+)/rocnik/novy/$',
        RocnikPridejView.as_view(),
        name='rocnik_pridani'),

    # UPDATEs
    url(r'^rozkategorizovat_zavodniky/(?P<rocnik_pk>\d+)/$',
        login_required(rozkategorizovat_zavodniky),
        name='rozkategorizovat_zavodniky'),
    url(r'^formular_startera/(?P<rocnik_pk>\d+)/$',
        login_required(formular_startera),
        name='formular_startera'),
    url(r'^zavod/(?P<pk>\d+)/editace/$',
        ZavodUpdateView.as_view(),
        name='zavod_editace'),
    url(r'^rocnik/(?P<pk>\d+)/editace/$',
        RocnikUpdateView.as_view(),
        name='rocnik_editace'),
    url(r'^kategorie/(?P<pk>\d+)/editace/$',
        KategorieUpdateView.as_view(),
        name='kategorie_editace'),

    # DELETE
    url(r'^rocnik/(?P<pk>\d+)/smazat/$',
        RocnikDeleteView.as_view(),
        name='rocnik_smazani'),
    url(r'^zavod/(?P<pk>\d+)/smazat/$',
        ZavodDeleteView.as_view(),
        name='zavod_smazani'),
    # url(r'^kategorie/(?P<pk>\d+)/smazat/$',
    #     KategorieDeleteView.as_view(),
    #     name='kategorie_smazani'),

    # FORMs
    url(r'^pridani_zavodniku/rocnik/(?P<pk>\d+)/$',
        login_required(pridani_zavodniku),
        name='pridani_zavodniku'),
    url(r'^import_zavodniku/rocnik/(?P<pk>\d+)/$',
        ImportZavodnikuView.as_view(),
        name='import_zavodniku'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/startovni_listina/$',
        startovni_listina,
        name='startovni_listina'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/startovni_listina/(?P<ordering_str>[-\w]+)/$',
        startovni_listina,
        name='startovni_listina'),
    url(r'^rocnik/(?P<pk>\d+)/startovni_casy/$',
        # login_required(startovni_casy),
        EditZavodniciView.as_view(),
        name='startovni_casy'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/cilovy_formular/$',
        login_required(cilovy_formular),
        name='cilovy_formular'),

    url(r'^rocnik/(?P<rocnik_pk>\d+)/startovka_export/$',
        startovka_export,
        name='startovka_export'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/startovka_export/(?P<ordering_str>[-\w]+)/$',
        startovka_export,
        name='startovka_export'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/vysledky_export/$',
        vysledky_export,
        name='vysledky_export'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/kategorie_export/$',
        kategorie_export,
        name='kategorie_export'),

    url(r'^kategorie/(?P<kategorie_pk>\d+)/pdf/vysledkova_listina/$',
        vysledky_kategorie_PDF,
        name='vysledky_kategorie_PDF'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/pdf/vysledkova_listina/$',
        vysledky_rocnik_PDF,
        name='vysledky_rocnik_PDF'),
    url(r'^kategorie/(?P<kategorie_pk>\d+)/pdf/startovni_listina/$',
        startovka_kategorie_PDF,
        name='startovka_kategorie_PDF'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/pdf/startovni_listina/$',
        startovka_rocnik_PDF,
        name='startovka_rocnik_PDF'),

    # AUTOCOMPLETEs
    url(r'^sport_autocomplete/$', sport_autocomplete, name='sport_autocomplete'),
    url(r'^zavod_autocomplete/$', zavod_autocomplete, name='zavod_autocomplete'),
)
