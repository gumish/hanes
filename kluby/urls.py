# coding: utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = patterns(
    '',
    # LISTs
    url(r'^$', KlubyListView.as_view(), name='kluby_list'),

    # DETAILs
    url(r'^detail/(?P<slug>[-\w]+)/$', KlubDetailView.as_view(), name='klub_detail'),
    url(r'^editace/(?P<slug>[-\w]+)/$', login_required(KlubUpdateView.as_view()), name='klub_update'),

    # AUTOCOMPLETEs
    url(r'^klub_autocomplete/$', klub_autocomplete, name='klub_autocomplete'),
)
