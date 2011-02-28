from django.db import models
from django.contrib.auth.models import User


class Feed(models.Model):
	url = models.URLField()
	title = models.CharField(max_length=255)
	updated = models.DateTimeField()


class Entry(models.Model):
	feed = models.ForeignKey(Feed, related_name='entries')
	uri = models.CharField(max_length=255)
	title = models.CharField(max_length=255)
	published = models.DateTimeField()
	updated = models.DateTimeField()
	summary = models.TextField()
	content = models.TextField()


class Subscription(models.Model):
	user = models.ForeignKey(User, related_name='reader_subscriptions')
	feed = models.ForeignKey(Feed, related_name='subscriptions')
	custom_title = models.CharField(max_length=255, blank=True, null=True)
	
	@property
	def title(self):
		return self.custom_title if self.custom_title else self.feed.title