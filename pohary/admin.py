from django.contrib import admin
from .models import Pohar, KategoriePoharu, BodoveHodnoceni, PocetZavoduPoharuSportu


class KategoriePoharuInline(admin.TabularInline):
    model = KategoriePoharu
    extra = 1


class PocetZavoduPoharuSportuInline(admin.TabularInline):
    model = PocetZavoduPoharuSportu
    extra = 1


@admin.register(Pohar)
class PoharAdmin(admin.ModelAdmin):
    list_display = ("nazev", "datum")
    inlines = [KategoriePoharuInline, PocetZavoduPoharuSportuInline]
    search_fields = ("nazev",)


admin.site.register(KategoriePoharu)
admin.site.register(BodoveHodnoceni)
