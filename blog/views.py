from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from blog.models import Post
from blog.forms import PostForm, CommentForm
from accounts.models import User


class BaseView(View):
    def get_context_data(self, *args, **kwargs):
        context = {}

        return context


@method_decorator([login_required], name='post')
class IndexView(BaseView):

    template_name = 'blog/index.html'

    def get(self, request):
        context = self.get_context_data()

        posts = Post.objects.order_by('-date')
        context['posts'] = posts

        return render(request, self.template_name, context)

    def post(self, request):
        post_form = PostForm(request.POST)
        context = self.get_context_data()

        posts = Post.objects.order_by('-date')
        context['posts'] = posts

        if post_form.is_valid():
            post_form.instance.author = User.objects.get(username=request.user.username)
            post_form.save()

            post_form = PostForm()

        return render(request, self.template_name, context)


@method_decorator([login_required], name='post')
class PostDetails(BaseView):

    template_name = 'blog/post-details.html'

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        context = self.get_context_data()
        context['post'] = post

        return render(request, self.template_name, context)

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)

        context = self.get_context_data()
        context['post'] = post

        user = User.objects.get(username=request.user.username)

        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment_form.instance.comment_author = user
            comment_form.save()

            post.comments.add(comment_form.instance)
            post.save()

            comment_form = CommentForm()

        return render(request, self.template_name, context)
