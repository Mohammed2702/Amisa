from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_author')
	title = models.CharField(max_length=30, blank=False)
	content = models.TextField(blank=False)
	date = models.DateTimeField(auto_now=True)
	updated = models.DateTimeField(auto_now_add=True)
	slug = models.SlugField(max_length=100, unique=True)

	def __str__(self):
		return self.title

	def get_absolute_url(self, *args, **kwargs):
		pass

	class Meta:
		verbose_name = 'Post'
		verbose_name_plural = 'Posts'
