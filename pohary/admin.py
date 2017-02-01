# coding: utf-8
from django.contrib import admin
from .models import Pohar, KategoriePoharu, BodoveHodnoceni


class KategoriePoharuInline(admin.TabularInline):
    model = KategoriePoharu
    extra = 1

class PoharAdmin(admin.ModelAdmin):
    list_display = ('nazev', 'datum')
    inlines = [
        KategoriePoharuInline,
    ]
    search_fields = ('nazev',)

admin.site.register(Pohar, PoharAdmin)
admin.site.register(KategoriePoharu)
admin.site.register(BodoveHodnoceni)
