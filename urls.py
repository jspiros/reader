from .views import home, lib, get_subscriptions, add_subscription, get_entries, read_entry
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('',
	url(r'^$', home, name='reader_home'),
	url(r'^lib.js$', lib, name='reader_lib'),
	url(r'^get_subscriptions$', get_subscriptions, name='reader_get_subscriptions'),
	url(r'^add_subscription$', add_subscription, name='reader_add_subscription'),
	url(r'^get_entries$', get_entries, name='reader_get_entries'),
	url(r'^read_entry$', read_entry, name='reader_read_entry'),
)