from django.http import HttpResponse

class ExceptionLoggingMiddleware(object):

    " middleware pro debug Ajaxu, upraveno pro Django 2.0.2 "

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        import traceback
        print(traceback.format_exc())
        return HttpResponse("in exception")
