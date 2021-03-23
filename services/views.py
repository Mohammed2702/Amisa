from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import threading
import os

from services.models import (
	Order,
	Network,
	Bank,
	Locator,
	Advert
)
from accounts.models import Wallet
from home.models import SiteSetting
from services.forms import (
	WithdrawalForm,
	DataForm,
    AdvertForm
)
from home.forms import SiteSettingForm
from Amisacb import utils
from Amisacb.context import external_context, user_features
from Amisacb.decorators import services_required, home_required


message_dir = os.path.join(settings.BASE_DIR, 'Amisacb/data/messages')


@login_required(login_url='accounts:account_signin')
def account_user_withdrawal(request):
    user_orders = [i for i in reversed(list(Order.objects.all()))]
    user_orders_truncate = [i for i in reversed(
        list(Order.objects.all()))][:5]

    context = {
        'user_orders': user_orders,
        'user_orders_truncate': user_orders_truncate,

    }
    template_name = 'Home/account_user_withdrawal.html'

    if request.method == 'POST':
        withdrawal_form = WithdrawalForm(request.POST)
        if withdrawal_form.is_valid():
            account_number = withdrawal_form.cleaned_data.get('account_number')
            account_name = withdrawal_form.cleaned_data.get('account_name')
            bank = withdrawal_form.cleaned_data.get('bank')
            amount = withdrawal_form.cleaned_data.get('amount')

            minimum_amount = SiteSetting.objects.get(pk=1).minimum_withdrawal
            reservation_amount = SiteSetting.objects.get(pk=1).reservation_amount

            if amount >= minimum_amount:
                if amount <= (request.user.wallet.wallet_balance - reservation_amount):
                    user_wallet = Wallet.objects.get(user=request.user)
                    description = f'{account_name}/ {bank}'
                    create_order = Order.objects.create(
                        user=request.user,
                        transaction='Withdrawal request',
                        amount=amount,
                        recipient=account_number,
                        description=description
                    )

                    if create_order:
                        user_wallet.wallet_balance -= amount

                        user_wallet.save()
                        create_order.save()

                        messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')
                        
                        mail_thread = threading.Thread(
                            target=utils.deliver_mail_order,
                            kwargs={
                                'title': '',
                                'body': description
                            }
                        )
                        mail_thread.start()
                        order_mail = utils.deliver_mail_order(
                            title='',
                            body=description
                        )

                        return redirect('services:account_user_withdrawal')
                    else:
                        messages.warning(request, 'Sorry, your request could not be processed at the moment')

                        return redirect('services:account_user_withdrawal')
                else:
                    messages.warning(request, f'Not sufficient funds, you can only withdraw {request.user.wallet.wallet_balance - reservation_amount} with your current balance')

                    return redirect('services:account_user_withdrawal')
            else:
                messages.warning(request, f'Least amount for Withdrawal is {minimum_amount}')

                return redirect('services:account_user_withdrawal')

    context = utils.dict_merge(
        external_context(),
        context,
        user_features(request.user.id),
        {
            'notice_notes': SiteSetting.objects.get(pk=1).withdrwal_note
        }
    )

    return render(request, template_name, context)


@login_required(login_url='accounts:account_signin')
def account_user_data(request):
    user_orders = [i for i in reversed(list(Order.objects.all()))]
    user_orders_truncate = [i for i in reversed(list(Order.objects.all()))][:5]

    template_name = 'Home/account_user_data.html'
    context = {
        'networks': [i.network for i in list(Network.objects.all())],
        'user_orders': user_orders,
        'user_orders_truncate': user_orders_truncate,

    }

    if request.method == 'POST':
        data_form = DataForm(request.POST)
        if data_form.is_valid():
            network = data_form.cleaned_data.get('network')
            user_phone = data_form.cleaned_data.get('phone_number')
            amount = data_form.cleaned_data.get('amount')

            minimum_amount = SiteSetting.objects.get(pk=1).minimum_data
            reservation_amount = SiteSetting.objects.get(pk=1).reservation_amount

            if amount >= minimum_amount:
                if (request.user.wallet.wallet_balance - reservation_amount) >= amount:
                    user_wallet = Wallet.objects.get(user=request.user)

                    description = f'Data/{network}'
                    create_order = Order.objects.create(
                        user=request.user,
                        transaction='Data purchase request',
                        amount=amount,
                        recipient=user_phone,
                        description=description
                    )

                    if create_order:
                        order_mail = utils.deliver_mail_order(
                            title='',
                            body=description
                        )
                        if order_mail:
                            user_wallet.wallet_balance -= amount

                            user_wallet.save()
                            create_order.save()

                            messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')
                        else:
                            create_order.delete()

                            messages.warning(request, f'''Your order couldn't be placed at the moment :(''')

                        return redirect('services:account_user_data')
                    else:
                        messages.warning(request, 'Sorry, your request could not be processed at the moment')

                        return redirect('services:account_user_data')
                else:
                    messages.warning(request, f'Not sufficient funds, you can only use {request.user.wallet.wallet_balance - reservation_amount} with your current balance')

                    return redirect('services:account_user_data')
            else:
                messages.warning(request, f'Least amount for Data is {minimum_amount}')

                return redirect('services:account_user_data')

    context = utils.dict_merge(
        external_context(),
        context,
        user_features(request.user.id),
        {
            'notice_notes': SiteSetting.objects.get(pk=1).data_note
        }
    )

    return render(request, template_name, context)


@login_required(login_url='accounts:account_signin')
def account_user_airtime(request):
    user_orders = [i for i in reversed(list(Order.objects.all()))]
    user_orders_truncate = [i for i in reversed(list(Order.objects.all()))][:5]
    template_name = 'Home/account_user_airtime.html'
    context = {
        'networks': [i.network for i in list(Network.objects.all())],
        'user_orders': user_orders,
        'user_orders_truncate': user_orders_truncate,

    }

    if request.method == 'POST':
        data_form = DataForm(request.POST)
        if data_form.is_valid():
            network = data_form.cleaned_data.get('network')
            user_phone = data_form.cleaned_data.get('phone_number')
            amount = data_form.cleaned_data.get('amount')

            minimum_amount = SiteSetting.objects.get(pk=1).minimum_airtime
            reservation_amount = SiteSetting.objects.get(pk=1).reservation_amount

            if amount >= minimum_amount:
                if (request.user.wallet.wallet_balance - reservation_amount) >= amount:
                    user_wallet = Wallet.objects.get(user=request.user)

                    description = f'Airtime/{network}'
                    create_order = Order.objects.create(
                        user=request.user,
                        transaction='Airtime purchase request',
                        amount=amount,
                        recipient=user_phone,
                        description=description
                    )

                    if create_order:
                        order_mail = utils.deliver_mail_order(
                            title='',
                            body=create_order.desc()
                        )

                        if order_mail:
                            user_wallet.wallet_balance -= amount

                            user_wallet.save()
                            create_order.save()

                            messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')
                        else:
                            create_order.delete()

                            messages.warning(request, f'''Your order couldn't be placed at the moment :(''')

                        return redirect('services:account_user_airtime')
                    else:
                        messages.warning(request, 'Sorry, your request could not be processed at the moment')

                        return redirect('services:account_user_airtime')
                else:
                    messages.warning(request, f'Not sufficient funds, you can only use {request.user.wallet.wallet_balance - reservation_amount} with your current balance')

                    return redirect('services:account_user_airtime')
            else:
                messages.warning(request, f'Least amount for Airtime is {minimum_amount}')

                return redirect('services:account_user_airtime')

    context = utils.dict_merge(
        external_context(),
        context,
        user_features(request.user.id),
        {
            'notice_notes': SiteSetting.objects.get(pk=1).airtime_note
        }
    )

    return render(request, template_name, context)


@services_required
@login_required(login_url='accounts:account_signin')
def show_all_orders(request):
    template_name = 'Home/show_all_orders.html'
    context = utils.dict_merge(external_context(), user_features(request.user.id))

    user_orders = [i for i in reversed(list(Order.objects.all().filter(user=request.user)))]
    user_orders_truncate = [i for i in reversed(list(Order.objects.all().filter(user=request.user))[:5])]
    admin_orders = [i for i in reversed(list(Order.objects.all()))]
    admin_orders_truncate = [i for i in reversed(list(Order.objects.all()))][:5]

    user_context = {
        'networks': [i.network for i in list(Network.objects.all())],
        'user_orders': user_orders,
        'user_orders_truncate': user_orders_truncate,
        'admin_orders': admin_orders,
        'admin_orders_truncate': admin_orders_truncate,

    }
    context = utils.dict_merge(context, user_context)

    return render(request, template_name, context)


@services_required
@login_required(login_url='accounts:account_signin')
def toggle_order(request, order_slug):
    if request.user.is_staff:
        order = Order.objects.get(slug=order_slug)

        if order.toggle_count <= 1:
            if order.status == 'processing':
                order.status = 'processed'
                order.toggle_count += 1

        order_message = open(f'{message_dir}/accept_order.txt', 'r').read().format(
            request.user.get_full_name,
            request.user.profile.reference_id,
            order.description
        )

        title = 'Order processed'
        body = order_message
        recipient = request.user.email

        email_success = utils.deliver_mail(
            title=title,
            body=body,
            recipient=recipient
        )

        if order:
            order.save()

        return redirect('services:show_all_orders')
    else:
        template_name = 'Home/404Error.html'
        return render(request, template_name)


@home_required
@login_required(login_url='accounts:account_signin')
def adverts(request):
    template_name = 'Home/adverts.html'
    context = utils.dict_merge(
        external_context(),
        user_features(request.user.id)
    )

    advert_form = AdvertForm(request.POST)

    if request.method == 'POST':
        if advert_form.is_valid():
            advert_form.save()
        else:
            print(advert_form.errors)

    return render(request, template_name, context)


@login_required(login_url='accounts:account_signin')
def adverts_list(request):
    template_name = 'Home/adverts_list.html'
    context = utils.dict_merge(
        external_context(),
        user_features(request.user.id),
        {
            'clients': Advert.objects.order_by('priority')
        }
    )

    return render(request, template_name, context)
