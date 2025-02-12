from django.http import JsonResponse
from django.template.loader import render_to_string

def disable_fields(form, fields: list):
    """
    Disables all fields in a form.

    Args:
        form: The form object.
        fields (list): A list of field names or field objects to be disabled.
            If a string is provided, the corresponding field in the form will be disabled.
            If a field object is provided, that field will be disabled.
    """
    for f in fields:
        if isinstance(f, str):
            form.fields[f].disabled = True
        else:
            f.field.disabled = True


class AjaxFormMixin():

    """ Obecny mixin pro 'ajax_???__???'

    Mixin pro views s 'generic.???', pracuje se sablonou a formularem.
    Nezajima ho zda-li jde o 'update' nebo 'create'.

    Attributes:
        update_selector <str>: odesle se do sablony, aby vedel jaky nejblizsi nadrazeny
            prvek ('closest()') html
        updated_template <path_str>: sablona pro updatovani prvnku v HTML po ulozeni do db
        form_template <str>: html sablona modal formulare
        jquery_function <str>: html / append / prepend / replaceWith
        form_title(str): dokonceni nazvu formulare 'vytvorit ....' / 'editovat ...: objekt'
        editing_page(str): pro sablony, kde se edit wrench ukazuje pouze pokud edit=True
        deletable(bool): zda-li se bude zobrazovat tlacitko pro smazani objektu
    https://www.codingforentrepreneurs.com/blog/ajaxify-django-forms/
    """

    form_template = None
    update_selector = None  # OPTIONAL: k nahrazeni rodice s timto selectorem, pokud neni vyplnen vezme se z nazvu sablony
    updated_template = None
    form_template = 'elements/_object_edit_modal_form.html'
    jquery_function = 'replaceWith'
    form_title = ''
    editing_page = True
    deletable = True

    def _get_json_form_html(self):

        """ vrati html formulare pro odeslani json """

        context = self.get_context_data()
        html_form = render_to_string(
            self.form_template,
            context,
            request=self.request)
        return {'html_form': html_form}


    def form_invalid(self, form):

        """ odesle vadny formular pres JSON """

        data = self._get_json_form_html()
        return JsonResponse(data, status=400)


    def form_valid(self, form):

        """ Ulozi objekt, odesle novy obsah sablony pro zmenu HTML stranky """

        self.object = form.save()
        context = self.get_context_data()
        new_html = render_to_string(
            self.updated_template,
            context,
            request=self.request)
        data = {
            'new_html': new_html
        }
        return JsonResponse(data)
