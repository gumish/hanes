import os
import sys

sys.path.append('d:')
sys.path.append('d:/WWW/PR/Hanes')

os.environ['DJANGO_SETTINGS_MODULE'] = 'Hanes.hanes.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIpointerler()
