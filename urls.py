from .views import home
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
	url(r'^$', home, name='reader_home'),
)