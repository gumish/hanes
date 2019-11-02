"""new URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('zavody/',
        include('zavody.urls', namespace='zavody')),
    path('lide/',
        include('lide.urls', namespace='lide')),
    path('kluby/',
        include('kluby.urls', namespace='kluby')),
    path('zavodnici/',
        include('zavodnici.urls', namespace='zavodnici')),
    path('pohary/',
        include('pohary.urls', namespace='pohary')),

    path('zalohovat_databazi/',
        login_required(views.backup_database), name='backup_database'),
    path('flatpages/editace/<int:pk>/',
        login_required(views.FlatPageUpdate.as_view()), name='flatpage_editace'),
    path('',
        views.uvod, {'url': '/uvod/'}, name='uvod'),

    # django
    path('admin/', admin.site.urls),
    path('accounts/',
        include('django.contrib.auth.urls')),
]

if settings.TEMPLATE_DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
