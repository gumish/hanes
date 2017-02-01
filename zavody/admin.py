# coding: utf-8
from django.contrib import admin

from .models import Sport, Zavod, Kategorie, Rocnik


class KategorieInline(admin.TabularInline):
    model = Kategorie
    extra = 0


class RocnikInline(admin.TabularInline):
    model = Rocnik
    extra = 0


class KategorieAdmin(admin.ModelAdmin):
    model = Kategorie
    list_display = ('nazev', 'znacka', 'pohlavi', 'vek_od', 'vek_do', 'delka_trate', 'rocnik', 'poradi')
    list_filter = ('pohlavi',)


class ZavodAdmin(admin.ModelAdmin):
    inlines = [RocnikInline]
    list_filter = ('sport', 'korekce_sezony')
    search_fields = ['nazev', 'slug']


class RocnikAdmin(admin.ModelAdmin):
    inlines = [KategorieInline]
    list_display = ('zavod', 'datum')
    list_filter = ('zavod',)
    search_fields = ['zavod']

admin.site.register(Zavod, ZavodAdmin)
admin.site.register(Kategorie, KategorieAdmin)
admin.site.register(Rocnik, RocnikAdmin)
admin.site.register(Sport)
