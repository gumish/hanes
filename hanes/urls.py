from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
# from django.contrib.flatpages import views
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .views import backup_database, uvod, FlatPageUpdate

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^zavody/', include('zavody.urls', namespace='zavody')),
    url(r'^lide/', include('lide.urls', namespace='lide')),
    url(r'^kluby/', include('kluby.urls', namespace='kluby')),
    url(r'^zavodnici/', include('zavodnici.urls', namespace='zavodnici')),
    url(r'^pohary/', include('pohary.urls', namespace='pohary')),

    url(r'^zalohovat_databazi/$', login_required(backup_database), name='backup_database'),
    url(r'^flatpages/editace/(?P<pk>[0-9]+)/$',
        login_required(FlatPageUpdate.as_view()), name='flatpage_editace'),
    url(r'^$', uvod, {'url': '/uvod/'}, name='uvod'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
)

urlpatterns += staticfiles_urlpatterns()

# urlpatterns += url(r'^(?P<url>.*/)$', views.flatpage),

if settings.TEMPLATE_DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
