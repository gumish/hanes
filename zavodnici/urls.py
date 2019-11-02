
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

app_name = 'zavodnici'
urlpatterns = [
    # UPDATEs
    path(
        'editace_zavodnika/<int:zavodnik_pk>/',
        login_required(editace_zavodnika),
        name='editace_zavodnika'),

    path(
        'rocnik/<int:rocnik_pk>/cislo_autocomplete/',
        cislo_autocomplete, name='cislo_autocomplete'),

    path(
        'uprav_zavodnika_ze_startovky/<int:pk>/',
        ZavodnikUpdateView.as_view(),
        name='uprav_zavodnika_ze_startovky'),

    path(
        'aktualizuj_data_startovky/<int:pk>/',
        login_required(aktualizuj_data_startovky),
        name='aktualizuj_data_startovky'),

    # DELETE
    path(
        'smaz_zavodnika_ze_startovky/<int:pk>/',
        login_required(smaz_zavodnika_ze_startovky),
        name='smaz_zavodnika_ze_startovky'),
]
