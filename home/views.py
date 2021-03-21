from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import *
from django.contrib.auth import *
from django.contrib import messages
from django.contrib.auth.decorators import *
from django.utils import timezone
from django.shortcuts import *
from django.conf import settings
from django.template import Context

from weasyprint import HTML

import requests
import random
import datetime
import pytz
import time
import os
import datetime

from home.forms import (
    LocatorForm,
    SiteSettingForm
)
from services.forms import (
    NetworkForm,
    BankForm
)
from home.models import (
    History,
    SiteSetting
)
from services.models import (
    Order,
    Locator,
    Bank,
    Network
)
from codes.models import (
    Code,
    CodeGroup
)
from Amisacb import utils
from Amisacb.context import user_features, external_context

# ENV
HOST_HEADER = 'https://'
DOMAIN = f'{HOST_HEADER}amisacb.pythonanywhere.com'
password_reset_main = f'{DOMAIN}/forgot_password'

message_dir = os.path.join(settings.BASE_DIR, 'Amisacb/data/messages')

User = get_user_model()


# Index

def index(request):
    template_name = 'index.html'
    context = {}
    context = utils.dict_merge(external_context(), context)

    return render(request, template_name, context)


@login_required(login_url='accounts:account_signin')
def code_group_codes(request, group_slug):
    if request.user.is_staff:
        template_name = 'Home/code_group_codes.html'

        group = CodeGroup.objects.get(slug=group_slug)
        code_group_children = list(Code.objects.all().filter(code_group=group))

        init_context = {
            'group': group,
            'code_group_children': code_group_children,
        }
        context = utils.dict_merge(external_context(), user_features(request.user.id))
        context = utils.dict_merge(init_context, context)

        return render(request, template_name, context)
    else:
        return render(request, 'Home/404Error.html')


@login_required(login_url='accounts:account_signin')
def site_settings(request):
    if request.user.is_superuser:
        get_setting = SiteSetting.objects.get(pk=1)
        if request.method == 'POST':
            settings_form = SiteSettingForm(request.POST)
            network_form = NetworkForm(request.POST)
            bank_form = BankForm(request.POST)

            if network_form.is_valid():
                network = network_form.cleaned_data.get('network')
                data_rate = network_form.cleaned_data.get('data_rate')

                if network not in [i.network for i in Network.objects.all()]:
                    create_network = Network.objects.create(
                        network=network,
                        data_rate=data_rate,
                    )

                    if create_network:
                        create_network.save()

                        messages.warning(request, f'{network} has been added to networks')
                    else:
                        messages.warning(request, f'{network} could not be added')
                else:
                    messages.warning(request, f'{network} already exist !!!')
            elif bank_form.is_valid():
                bank = bank_form.cleaned_data.get('bank')

                if bank not in [i.bank for i in Bank.objects.all()]:
                    create_bank = Bank.objects.create(
                        bank=bank
                    )

                    create_bank.save()

                    messages.info(request, f'Bank ({bank}) added')
                else:
                    messages.info(request, f'{bank} already exist')

            elif settings_form.is_valid():
                customer_rate = settings_form.cleaned_data.get('customer_rate')
                services_note = settings_form.cleaned_data.get('services_note')
                minimum_withdrawal = settings_form.cleaned_data.get('minimum_withdrawal')
                minimum_airtime = settings_form.cleaned_data.get('minimum_airtime')
                minimum_data = settings_form.cleaned_data.get('minimum_data')
                reservation_amount = settings_form.cleaned_data.get('reservation_amount')
                call_contact = settings_form.cleaned_data.get('call_contact')
                whatsapp_contact = settings_form.cleaned_data.get('whatsapp_contact')
                email_contact = settings_form.cleaned_data.get('email_contact')
                how_to = settings_form.cleaned_data.get('how_to')
                about_us = settings_form.cleaned_data.get('about_us')
                terms_of_use = settings_form.cleaned_data.get('terms_of_use')
                faq = settings_form.cleaned_data.get('faq')

                get_setting.customer_rate = customer_rate
                get_setting.services_note = services_note
                get_setting.minimum_withdrawal = minimum_withdrawal
                get_setting.minimum_airtime = minimum_airtime
                get_setting.minimum_data = minimum_data
                get_setting.reservation_amount = reservation_amount
                get_setting.call_contact = call_contact
                get_setting.whatsapp_contact = whatsapp_contact
                get_setting.email_contact = email_contact
                get_setting.how_to = how_to
                get_setting.about_us = about_us
                get_setting.terms_of_use = terms_of_use
                get_setting.faq = faq

                get_setting.save()

                messages.warning(request, 'Settings Update Successful !!!')

        else:
            settings_form = SiteSettingForm(request.POST)
            network_form = NetworkForm(request.POST)
            bank_form = BankForm(request.POST)

        template_name = 'Home/site_settings.html'
        context = utils.dict_merge(external_context(), user_features(request.user.id))
        context = utils.dict_merge(context, {'settings_form': settings_form, 'get_setting': get_setting})

        return render(request, template_name, context)
    else:
        return render(request, 'Home/404Error.html')
    return redirect('Home:site_settings')


def all_posts(request):
    try:
        get_all_posts = [i for i in reversed(list(Post.objects.all()))]

        user_context = {
            'all_posts': get_all_posts,

        }
        context = utils.dict_merge(
            user_context, user_features(request.user.id))

        template_name = 'Home/posts.html'

        if request.method == 'POST':
            if request.user.is_staff:
                post_form = PostForm(request.POST)
                context = utils.dict_merge(context, {'post_form': post_form})
                if post_form.is_valid():
                    post_title = post_form.cleaned_data.get('post_title')
                    post_content = post_form.cleaned_data.get('post_content')

                    create_post = Post.objects.create(
                        author=request.user,
                        title=post_title,
                        content=post_content,
                    )

                    if create_post:
                        create_post.save()

                        messages.info(request, 'Post was successfully created.')

                        return redirect('Home:posts')
                    else:
                        messages.info(request, 'Post could not be created.')

                        return redirect('Home:posts')
            else:
                return render(request, 'Home/404Error.html')
        else:
            post_form = PostForm()
            context = utils.dict_merge(context, {'post_form': post_form})

        context = utils.dict_merge(external_context(), context)

        return render(request, template_name, context)
    except Exception as e:
        print('all_posts', e)


def post_detail(request, post_id):
    try:
        pass
    except Exception as e:
        print('post_detail', e)


@login_required(login_url='accounts:account_signin')
def post_edit(request, post_id):
    try:
        pass
    except Exception as e:
        print('post_edit', e)


@login_required(login_url='accounts:account_signin')
def post_delete(request, post_id):
    try:
        if request.user.is_staff:
            post = Post.objects.get(pk=post_id)
            post.delete()

            messages.info(request, 'Post was successfully deleted :)')

            return redirect('Home:posts')
        else:
            return render(request, 'Home/404Error.html')
    except Post.DoesNotExist:
        return render(request, 'Home/404Error.html')
    except Exception as e:
        print('post_delete', e)


# Extras


def charges_and_pricing(request):
    try:
        if str(request.user) != 'AnonymousUser':
            user_orders = [i for i in reversed(
                list(Order.objects.all().filter(user=request.user)))]
            user_orders_truncate = [i for i in reversed(
                list(Order.objects.all().filter(user=request.user))[:5])]
            admin_orders = [i for i in reversed(
                list(Order.objects.all()))]
            admin_orders_truncate = [i for i in reversed(
                list(Order.objects.all()))][:5]

            user_context = {
                'user_orders': user_orders,
                'user_orders_truncate': user_orders_truncate,
                'admin_orders': admin_orders,
                'admin_orders_truncate': admin_orders_truncate,

            }
            context = user_context
            context = utils.dict_merge(external_context(), context)

            user_details = utils.dict_merge(
                user_features(request.user.id), context)
            context = utils.dict_merge(external_context(), user_details)

            template_name = 'Home/charges_and_pricing.html'

            return render(request, template_name, context)
        else:
            user_context = {
            }
            context = user_context

            template_name = 'Home/charges_and_pricing.html'

            return render(request, template_name, context)
    except Exception as e:
        print('charges_and_pricing', e)


def terms_of_use(request):
    if str(request.user) != 'AnonymousUser':
        print(type(request.user), 'True')
        user_orders = [i for i in reversed(
            list(Order.objects.all().filter(user=request.user)))]
        user_orders_truncate = [i for i in reversed(
            list(Order.objects.all().filter(user=request.user))[:5])]
        admin_orders = [i for i in reversed(
            list(Order.objects.all()))]
        admin_orders_truncate = [i for i in reversed(
            list(Order.objects.all()))][:5]

        user_context = {
            'user_orders': user_orders,
            'user_orders_truncate': user_orders_truncate,
            'admin_orders': admin_orders,
            'admin_orders_truncate': admin_orders_truncate,

        }
        context = user_context
        context = utils.dict_merge(external_context(), context)

        user_details = utils.dict_merge(
            user_features(request.user.id), context)
        context = utils.dict_merge(external_context(), user_details)

        template_name = 'Home/terms_of_use.html'

        return render(request, template_name, context)
    else:
        print(request.user)
        user_context = {

        }
        context = user_context

        template_name = 'Home/terms_of_use.html'

        return render(request, template_name, context)



@login_required(login_url='accounts:account_signin')
def locator(request):
    template_name = 'Home/locator.html'
    context = utils.dict_merge(
        external_context(),
        user_features(request.user.id)
    )
    
    locator_form = LocatorForm(request.POST)

    if request.method == 'POST':
        if locator_form.is_valid():
            if 'add-new' in locator_form.data:
                location = locator_form.cleaned_data.get('location')
                information = locator_form.cleaned_data.get('information')

                locator = Locator.objects.create(
                    location=location,
                    information=information
                )

                locator.save()

                messages.success(request, 'New Location added :)')
            if 'edit-locator' in locator_form.data:
                id_ = locator_form.cleaned_data.get('id_')
                location = locator_form.cleaned_data.get('location')
                information = locator_form.cleaned_data.get('information')

                locator = Locator.objects.get(pk=id_)
                locator.location = location
                locator.information = information

                locator.save()

                messages.info(request, 'Location updated :)')
            if 'delete-locator' in locator_form.data:
                id_ = locator_form.cleaned_data.get('id_')

                locator = Locator.objects.get(pk=id_)
                locator.delete()

                messages.info(request, 'Location deleted :)')

        return redirect('Home:locator')
    else:
        location_form = LocatorForm()

    context = utils.dict_merge(
        context,
        {
            'location_form': location_form
        }
    )

    return render(request, template_name, context)
