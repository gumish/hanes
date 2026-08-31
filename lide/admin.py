
from django.contrib import admin
from django.db.models import Count

from .models import Clenstvi, Clovek, Stat


class ClenstviInline(admin.TabularInline):
    model = Clenstvi
    extra = 0

class StatAdmin(admin.ModelAdmin):
    list_display = ('nazev', 'zkratka', 'poradi')
    list_editable = ('poradi',)

admin.site.register(Stat, StatAdmin)


class ClovekAdmin(admin.ModelAdmin):
    list_display = ('prijmeni', 'jmeno', 'narozen', 'pohlavi', 'slug', 'pocet_zavodu')
    list_filter = ('pohlavi',)
    search_fields = ('prijmeni', 'jmeno', 'clenstvi__klub__nazev')
    inlines = (ClenstviInline,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(zavodu=Count('zavodnici'))

    def pocet_zavodu(self, obj):
        return obj.zavodu
    pocet_zavodu.admin_order_field = 'zavodu'
    pocet_zavodu.short_description = 'Počet závodů'


admin.site.register(Clovek, ClovekAdmin)
admin.site.register(Clenstvi)
