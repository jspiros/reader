from .models import Feed, Entry
import datetime
import feedparser


def refresh_feed(feed, save=True):
	if feed.alive:
		parsed = feedparser.parse(feed.url, etag=feed.etag, modified=(feed.modified.timetuple() if feed.modified else None))
		if parsed.get('status', None) == 304:
			return
		if parsed.get('status', None) == 301 and parsed.has_key('href'):
			feed.url = parsed.href
		if parsed.get('status', None) == 410:
			feed.alive = False
		if parsed.has_key('etag'):
			feed.etag = parsed.etag
		if parsed.has_key('modified'):
			feed.modified = datetime.datetime(*(parsed.modified[0:6]))
		feed.title = parsed.feed.get('title', feed.url)
		feed.updated = datetime.datetime(*(parsed.feed.get('updated_parsed', datetime.datetime.now().timetuple())[0:6]))
		if save:
			feed.save()


def add_feed(url):
	feed = Feed(url=url)
	refresh_feed(feed)
	return feed