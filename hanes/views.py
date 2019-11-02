
import os
import datetime
import shutil
from django.views.generic.edit import UpdateView
from django.contrib.flatpages.models import FlatPage
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse

from zavody.models import Rocnik
from .settings import BASE_DIR, DATABASES


def uvod(request, url):
    try:
        uvod = FlatPage.objects.get(url=url)
    except FlatPage.DoesNotExist:
        uvod = None

    dnes = datetime.date.today()
    start = dnes - datetime.timedelta(dnes.weekday())
    konec = start + datetime.timedelta(7)
    zavody_seznam = (
        reversed(Rocnik.objects.filter(datum__gt=konec).order_by('datum')[:3]),  # za tyden a dal (max 3)
        Rocnik.objects.filter(datum__range=(start, konec)).exclude(datum=dnes),  # tento tyden
        Rocnik.objects.filter(datum=dnes),  # dnes
        Rocnik.objects.filter(datum__lt=start)[:5]  # minulych pet zavodu
    )
    return render(request,
        'uvod.html',
        {
            'flatpage': uvod,
            'zavody_seznam': zavody_seznam,
        })


class FlatPageUpdate(UpdateView):
    model = FlatPage
    fields = ['title', 'content']
    template_name = 'objekt_editace.html'


def backup_database(request):
    "kopiruje databazovy soubor, ciselne indexuje"
    delimiter = '__'
    src_path = DATABASES['default']['NAME']
    filename, ext = os.path.splitext(os.path.split(src_path)[1])
    dest_folder = os.path.join(BASE_DIR, '_BACKUP_')
    files = os.listdir(dest_folder)
    if files:
        last_file = os.path.splitext(files[-1])[0]
        try:
            new_number = int(last_file.split(delimiter)[1]) + 1
        except:
            new_number = 0
    else:
        new_number = 0
    new_index = str(new_number).zfill(3)
    new_filename = filename + delimiter + new_index + ext
    dest_path = os.path.join(dest_folder, new_filename)
    shutil.copy(src_path, dest_path)
    return HttpResponse('databázový soubor zálohován')
