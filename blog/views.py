from django.shortcuts import render
from django.views import View


class BaseView(View):
	def get_context_data(self, *args, **kwargs):
		context = {}

		return context


class IndexView(BaseView):
	template_name = 'blog/index.html'

	def get(self, request):
		context = self.get_context_data()

		return render(request, self.template_name, context)
