
from django.contrib import admin

from .models import Zavodnik
from zavody.models import Kategorie


class ZavodnikAdmin(admin.ModelAdmin):
    list_display = ('clovek', 'rocnik', 'kategorie', 'cislo', 'vysledny_cas')
    list_filter = ('rocnik__zavod',)
    search_fields = ('clovek__jmeno', 'clovek__prijmeni')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        'omezeni listu kategorii na kategorie aktualniho zavodu'
        if db_field.name == 'kategorie':
            # ziskani aktualniho zavodnika, druhy argument ziska ID zavodnika z URL
            try:
                zavodnik = self.get_object(request, request.resolver_match.args[0])
                kwargs["queryset"] = Kategorie.objects.filter(zavod=zavodnik.rocnik.zavod)
            except:
                pass
        return super(ZavodnikAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Zavodnik, ZavodnikAdmin)
