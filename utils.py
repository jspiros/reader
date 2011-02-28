from .models import Feed, Entry
import datetime
import feedparser


def refresh_feed(feed, save=True):
	parsed = feedparser.parse(feed.url)
	feed.title = parsed.feed.get('title', feed.url)
	feed.updated = datetime.datetime(*(parsed.feed.get('updated_parsed', datetime.datetime.now().timetuple())[0:6]))
	if save:
		feed.save()


def add_feed(url):
	feed = Feed(url=url)
	refresh_feed(feed)
	return feed