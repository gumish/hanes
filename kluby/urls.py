
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

app_name = 'kluby'
urlpatterns = [
    # LISTs
    path('',
        KlubyListView.as_view(), name='kluby_list'),

    # DETAILs
    path('detail/<str:slug>/',
        KlubDetailView.as_view(), name='klub_detail'),
    path('editace/<str:slug>/',
        login_required(KlubUpdateView.as_view()), name='klub_update'),

    # AUTOCOMPLETEs
    path('klub_autocomplete/',
        klub_autocomplete, name='klub_autocomplete'),
]
