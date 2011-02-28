from .models import Feed, Entry
import datetime
import feedparser


def _rate_content(content):
	if content.type == 'application/xhtml+xml':
		return 0
	elif content.type == 'text/html':
		return 1
	elif content.type == 'text/plain':
		return 2
	else:
		return 3


def _choose_content(contents):
	limited_contents = [content for content in contents if content.type in ('application/xhtml+xml', 'text/html', 'text/plain')]
	limited_contents.sort(key=_rate_content)
	return limited_contents[0] if len(limited_contents) > 0 else None


def _parse_date(date):
	try:
		return datetime.datetime(*(date[0:6]))
	except:
		return None


def _add_entry(feed, parsed_entry):
	title = parsed_entry.get('title', 'Untitled')
	link = parsed_entry.get('link', feed.link)
	published = _parse_date(parsed_entry.get('published_parsed', parsed_entry.get('created_parsed', parsed_entry.get('updated_parsed', None))))
	if not published:
		published = datetime.datetime.now()
	updated = _parse_date(parsed_entry.get('updated_parsed', None))
	if not updated:
		updated = published
	contents = parsed_entry.get('content', None)
	if contents:
		content = _choose_content(contents).value
	else:
		content = None
	summary = parsed_entry.get('summary', None)
	
	if summary or content:
		entry, created = feed.entries.get_or_create(uri=parsed_entry.id, defaults={
			'title': title,
			'link': link,
			'published': published,
			'updated': updated,
			'summary': summary,
			'content': content
		})
		if not created:
			entry.title = title
			entry.link = link
			entry.published = published
			entry.updated = updated
			entry.summary = summary
			entry.content = content
			entry.save()


def _add_entries(feed, parsed):
	for parsed_entry in parsed.entries:
		_add_entry(feed, parsed_entry)


def refresh_feed(feed):
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
		feed.updated = _parse_date(parsed.feed.get('updated_parsed', datetime.datetime.now().timetuple())[0:6])
		feed.link = parsed.feed.get('link', feed.url)
		
		feed.save()
		_add_entries(feed, parsed)


def refresh_all_feeds():
	for feed in Feed.objects.all():
		refresh_feed(feed)


def add_feed(url):
	feed = Feed(url=url)
	refresh_feed(feed)
	return feed