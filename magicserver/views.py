__author__ = 'VanLinh'

from django.template import Context, loader
from django.http import HttpResponse

def index(request):

    return HttpResponse('Hello from twisted django')