
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

app_name='lide'
urlpatterns = [
    # LISTs
    path('',
        clovek_list, name='lide_list'),

    # DETAILs
    path('detail/<str:slug>/',
        ClovekDetailView.as_view(), name='clovek_detail'),
    path('editace/<str:slug>/',
        login_required(clovek_update), name='clovek_update'),

    # IMPORTs
    path('import_csv/',
        LideImportCSV.as_view(), name='import_csv'),

    # AUTOCOMPLETEs
    path('clovek_autocomplete/',
        clovek_autocomplete, name='clovek_autocomplete'),
    path('rocnik/<int:rocnik_pk>/clovek_autocomplete/',
        clovek_autocomplete, name='clovek_autocomplete'),

    # UTILITY
    path('duplicity/',
        duplicity, name='duplicity'),
]
