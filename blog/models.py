from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_author')
	title = models.CharField(max_length=30, blank=False)
	content = models.TextField(blank=False)
	comments = models.ManyToManyField('Comment')
	likes = models.ManyToManyField('Like')
	date = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	slug = models.SlugField(max_length=100, unique=True)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.slug:
			import secrets

			self.slug = secrets.token_urlsafe(40)

		super().save(*args, **kwargs)

	def get_absolute_url(self, *args, **kwargs):
		pass

	class Meta:
		verbose_name = 'Post'
		verbose_name_plural = 'Posts'


class Comment(models.Model):
	comment_author = models.ForeignKey(User, on_delete=models.CASCADE)
	comment = models.TextField()
	slug = models.SlugField(max_length=100, unique=True, blank=True)
	date = models.DateTimeField(auto_now=True)
	updated = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.comment_author.username

	def save(self, *args, **kwargs):
		if not self.slug:
			import secrets

			self.slug = secrets.token_urlsafe(40)

		super().save(*args, **kwargs)

	class Meta:
		verbose_name = 'Comment'
		verbose_name_plural = 'Comments'


class Like(models.Model):
	like_author = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.like_author.username

	class Meta:
		verbose_name = 'Like'
		verbose_name_plural = 'Likes'
