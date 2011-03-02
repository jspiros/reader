from django.db import models
from django.contrib.auth.models import User


class Feed(models.Model):
	url = models.URLField()
	title = models.CharField(max_length=255)
	link = models.URLField(blank=True, null=True)
	updated = models.DateTimeField()
	etag = models.CharField(max_length=255, blank=True, null=True)
	modified = models.DateTimeField(blank=True, null=True)
	alive = models.BooleanField(default=True)
	
	def __unicode__(self):
		return u'%s <%s>' % (self.title, self.url)


class Entry(models.Model):
	feed = models.ForeignKey(Feed, related_name='entries')
	uri = models.CharField(max_length=255)
	title = models.CharField(max_length=255)
	link = models.URLField(blank=True, null=True)
	published = models.DateTimeField()
	updated = models.DateTimeField()
	summary = models.TextField(blank=True, null=True)
	content = models.TextField(blank=True, null=True)
	
	class Meta:
		verbose_name_plural = 'entries'
		ordering = ['-published']
	
	def __unicode__(self):
		return u'%s <%s>' % (self.title, self.feed)


class Subscription(models.Model):
	user = models.ForeignKey(User, related_name='reader_subscriptions')
	feed = models.ForeignKey(Feed, related_name='subscriptions')
	custom_title = models.CharField(max_length=255, blank=True, null=True)
	
	@property
	def title(self):
		return self.custom_title if self.custom_title else self.feed.title
	
	def __unicode__(self):
		return u'%s <%s>' % (self.user, self.feed)


class UserEntry(models.Model):
	user = models.ForeignKey(User, related_name='reader_userentries')
	entry = models.ForeignKey(Entry, related_name='userentries')
	read = models.BooleanField(default=False)
	
	class Meta:
		verbose_name = 'user entry relationship'
		verbose_name_plural = 'user entry relationships'
	
	def __unicode__(self):
		return u'%s <%s>' % (self.user, self.entry)