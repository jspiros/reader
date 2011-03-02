from .models import Feed, Entry, Subscription, UserEntry
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from django.db.models import Q
from .utils import add_feed, unread_count


@login_required
def lib(request):
	return render_to_response('reader/lib.js', context_instance=RequestContext(request), mimetype='text/javascript')


@login_required
def home(request):
	return render_to_response('reader/home.html', {
		'entries': Entry.objects.filter(feed__subscriptions__user=request.user),
		'feeds': Feed.objects.filter(subscriptions__user=request.user),
	}, context_instance=RequestContext(request))


@login_required
def get_subscriptions(request):
	root = []
	for subscription in Subscription.objects.filter(user=request.user):
		root.append({
			'id': subscription.pk,
			'type': 'feed',
			'title': subscription.title,
			'unread': unread_count(request.user, feed=subscription.feed)
		})
	root.append({
		'id': -2,
		'type': 'all',
		'title': 'All Entries',
		'unread': unread_count(request.user),
	})
	root.append({
		'id': -1,
		'type': 'unread',
		'title': 'Unread Entries',
		'unread': unread_count(request.user),
	})
	root.sort(key=lambda sub: sub['id'])
	
	return HttpResponse(json.dumps({'len': len(root), 'root': root}), mimetype='application/json')


@login_required
def add_subscription(request):
	try:
		url = request.POST['url']
		add_feed(url, user=request.user)
		return HttpResponse()
	except:
		raise Http404


@login_required
def get_entries(request):
	if 'subscription_id' in request.POST:
		subscription_id = str(request.POST['subscription_id'])
		if subscription_id == '-2':
			entries = Entry.objects.filter(feed__subscriptions__user=request.user)
		elif subscription_id == '-1':
			entries = Entry.objects.filter(feed__subscriptions__user=request.user).exclude(userentries__user=request.user, userentries__read=True)
		elif subscription_id.startswith('tag:'):
			pass
		else:
			try:
				subscription = Subscription.objects.get(user=request.user, id=subscription_id)
				entries = subscription.feed.entries.all()
			except Subscription.DoesNotExist:
				raise Http404
	else:
		raise Http404
	
	root = []
	for entry in entries:
		root.append({
			'id': entry.pk,
			'title': entry.title,
			'date': entry.published.isoformat(),
			'content': entry.content if entry.content else entry.summary,
			'link': entry.link if entry.link else entry.feed.link,
		})
	root.sort(key=lambda entry: entry['date'])
	root.reverse()
	
	return HttpResponse(json.dumps({'len': len(root), 'root': root}), mimetype='application/json')


@login_required
def read_entry(request):
	if 'entry_id' in request.POST:
		entry = Entry.objects.get(id=request.POST['entry_id'])
		userentry, created = UserEntry.objects.get_or_create(entry=entry, user=request.user, defaults={ 'read': True })
		if not created:
			userentry.read = True
			userentry.save()
	else:
		raise Http404
	
	return HttpResponse()