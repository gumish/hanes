from django.urls import path
from . import views


app_name = 'pohary'
urlpatterns = [
    # LISTs
    path('',
        views.PoharyListView.as_view(),
        name='pohary_list'),

    # DETAILs
    path('detail/<str:slug>/',
        views.PoharDetailView.as_view(),
        name='pohar_detail'),
    path('kategorie/<int:pk>/',
        views.KategoriePoharuDetailView.as_view(),
        name='kategorie-poharu_detail'),
    path('pridat/',
        views.PoharCreateView.as_view(),
        name='pohar_create'),
]
