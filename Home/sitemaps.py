from django.contrib.sitemaps import Sitemap
# from django.urls import reverse
from django.shortcuts import reverse
from . import models


class PostSitemap(Sitemap):
	def items(self):
		return models.Post.objects.all()


class StaticViewSitemap(Sitemap):
	def items(self):
		return ['Home:faq']

	def location(self, item):
		return reverse(item)
