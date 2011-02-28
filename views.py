from .models import Feed, Entry
from django.shortcuts import render_to_response
from django.template import RequestContext


def home(request):
	return render_to_response('reader/home.html', {
		'entries': Entry.objects.all(),
		'feeds': Feed.objects.all(),
	}, context_instance=RequestContext(request))