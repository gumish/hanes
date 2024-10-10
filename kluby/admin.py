
from django.contrib import admin

from .models import Klub
from lide.models import Clenstvi


class ClenInline(admin.TabularInline):
    model = Clenstvi
    extra = 0


class KlubAdmin(admin.ModelAdmin):
    inlines = [ClenInline]
    search_fields = ['nazev', 'zkratka']

admin.site.register(Klub, KlubAdmin)
