# coding: utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = patterns(
    '',
    # LISTs
    url(r'^$', clovek_list, name='lide_list'),

    # DETAILs
    url(r'^detail/(?P<slug>[-\w]+)/$', ClovekDetailView.as_view(), name='clovek_detail'),
    url(r'^editace/(?P<slug>[-\w]+)/$', login_required(clovek_update), name='clovek_update'),

    # IMPORTs
    url(r'^import_csv/$', LideImportCSV.as_view(), name='import_csv'),

    # AUTOCOMPLETEs
    url(r'^clovek_autocomplete/$', clovek_autocomplete, name='clovek_autocomplete'),
    url(r'^rocnik/(?P<rocnik_pk>\d+)/clovek_autocomplete/$', clovek_autocomplete, name='clovek_autocomplete'),

    # UTILITY
    url(r'^duplicity/$', duplicity, name='duplicity'),
)
