from django.urls import path, include
from django.contrib.auth.decorators import login_required

from .views import *

app_name='zavody'
urlpatterns = [
    # LISTs
    path('',
        ZavodyListView.as_view(),
        name='zavody_list'),

    # DETAILs
    path('detail/<int:pk>/',
        ZavodDetailView.as_view(),
        name='zavod_detail'),
    path('rocnik/<int:pk>/detail/',
        RocnikDetailView.as_view(),
        name='rocnik_detail'),
    path('rocnik/<int:pk>/startovne/',
        StartovneRocnikuDetailView.as_view(),
        name='startovne_rocniku_detail'),
    path('kategorie/<int:pk>/',
        KategorieDetailView.as_view(),
        name='kategorie_detail'),
    path('rocnik/<int:rocnik_pk>/vysledkova_listina/',
        vysledkova_listina,
        name='vysledkova_listina'),
    path('rocnik/<int:pk>/startovni_casy/',
        login_required(StartovniCasyView.as_view()),
        name='startovni_casy'),

    # CREATEs
    path('zavod/novy/',
        ZavodPridejView.as_view(),
        name='zavod_pridani'),
    path('<str:slug>/rocnik/novy/',
        RocnikPridejView.as_view(),
        name='rocnik_pridani'),

    # UPDATEs
    path('rozkategorizovat_zavodniky/<int:rocnik_pk>/',
        login_required(rozkategorizovat_zavodniky),
        name='rozkategorizovat_zavodniky'),
    path('formular_startera/<int:rocnik_pk>/',
        login_required(formular_startera),
        name='formular_startera'),
    path('zavod/<int:pk>/editace/',
        ZavodUpdateView.as_view(),
        name='zavod_editace'),
    path('rocnik/<int:pk>/editace/',
        RocnikUpdateView.as_view(),
        name='rocnik_editace'),
    path('kategorie/<int:pk>/editace/',
        KategorieUpdateView.as_view(),
        name='kategorie_editace'),

    # DELETE
    path('rocnik/<int:pk>/smazat/',
        RocnikDeleteView.as_view(),
        name='rocnik_smazani'),
    path('zavod/<int:pk>/smazat/',
        ZavodDeleteView.as_view(),
        name='zavod_smazani'),
    # path('kategorie/<int:pk>/smazat/',
    #     KategorieDeleteView.as_view(),
    #     name='kategorie_smazani'),

    # FORMs
    path('pridani_zavodniku/rocnik/<int:pk>/',
        login_required(pridani_zavodniku),
        name='pridani_zavodniku'),
    path('import_zavodniku/rocnik/<int:pk>/',
        login_required(ImportZavodnikuView.as_view()),
        name='import_zavodniku'),
    path('rocnik/<int:rocnik_pk>/startovni_listina/',
        startovni_listina,
        name='startovni_listina'),
    path('rocnik/<int:rocnik_pk>/startovni_listina/<str:ordering_str>/',
        startovni_listina,
        name='startovni_listina'),
    path('rocnik/<int:rocnik_pk>/cilovy_formular/',
        login_required(cilovy_formular),
        name='cilovy_formular'),
    path('rocnik/<int:rocnik_pk>/import_souboru_casu/txt/',
        login_required(ImportCasuSouborView.as_view()),
        name='import_souboru_casu_txt'),
    path('rocnik/<int:rocnik_pk>/import_textu_casu/',
        login_required(ImportCasuTextView.as_view()),
        name='import_textu_casu'),
    path('rocnik/<int:rocnik_pk>/zpracovani_importovanych_casu/txt/',
        login_required(ZpracovaniImportovanychCasuTxtView.as_view()),
        name='zpracovani_importovanych_casu_txt'),

    # AJAX
    path('kategorie/<int:pk>/startovni_casy/upravit/',
        login_required(AjaxKategorieStartovniCasyUpdateView.as_view()),
        name='ajax_kategorie_startovni_casy_update'),

    # EXPORT
    path('rocnik/<int:rocnik_pk>/startovka_export/',
        startovka_export,
        name='startovka_export'),
    path('rocnik/<int:rocnik_pk>/startovka_export/<str:ordering_str>/',
        startovka_export,
        name='startovka_export'),
    path('rocnik/<int:rocnik_pk>/vysledky_export/',
        vysledky_export,
        name='vysledky_export'),
    path('rocnik/<int:rocnik_pk>/kategorie_export/',
        kategorie_export,
        name='kategorie_export'),

    path('kategorie/<int:kategorie_pk>/pdf/vysledkova_listina/',
        vysledky_kategorie_PDF,
        name='vysledky_kategorie_PDF'),
    path('rocnik/<int:rocnik_pk>/pdf/vysledkova_listina/',
        vysledky_rocnik_PDF,
        name='vysledky_rocnik_PDF'),
    path('kategorie/<int:kategorie_pk>/pdf/startovni_listina/',
        startovka_kategorie_PDF,
        name='startovka_kategorie_PDF'),
    path('rocnik/<int:rocnik_pk>/pdf/startovni_listina/',
        startovka_rocnik_PDF,
        name='startovka_rocnik_PDF'),

    # AUTOCOMPLETEs
    path('sport_autocomplete/', sport_autocomplete, name='sport_autocomplete'),
    path('zavod_autocomplete/', zavod_autocomplete, name='zavod_autocomplete'),
]
