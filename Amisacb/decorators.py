# apps
# - services
# - codes
# - accounts
# - blog
# - home


from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def services_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='accounts:account_signin'):
    actual_decorator = user_passes_test(
        lambda user: user.is_services,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


def codes_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='accounts:account_signin'):
    actual_decorator = user_passes_test(
        lambda user: user.is_services,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


def accounts_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='accounts:account_signin'):
    actual_decorator = user_passes_test(
        lambda user: user.is_account,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


def blog_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='accounts:account_signin'):
    actual_decorator = user_passes_test(
        lambda user: user.is_blog,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


def home_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='accounts:account_signin'):
    actual_decorator = user_passes_test(
        lambda user: user.is_home,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator
