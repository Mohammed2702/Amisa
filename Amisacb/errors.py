from django.shortcuts import render

# Errors


def custom_404(request, exception=None):
    return render(request, template_name='Home/404Error.html')


def custom_500(request, exception=None):
    return render(request, template_name='Home/500Error.html')


def custom_403(request, exception=None):
    return render(request, template_name='Home/403Error.html')


def custom_400(request, exception=None):
    return render(request, template_name='Home/400Error.html')
