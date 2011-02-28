from .models import Feed, Entry, Subscription
from django.contrib import admin


admin.site.register((Feed, Entry, Subscription))