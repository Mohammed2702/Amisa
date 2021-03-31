from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
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
    AirtimeForm,
    AdvertForm
)
from services.utils import API
from Amisacb import utils
from Amisacb.context import external_context, user_features
from Amisacb.decorators import services_required, home_required


message_dir = os.path.join(settings.BASE_DIR, 'Amisacb/data/messages')


@login_required
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

            transaction_id = API().make_transaction_id()

            minimum_amount = SiteSetting.objects.get(pk=1).minimum_withdrawal
            reservation_amount = SiteSetting.objects.get(pk=1).reservation_amount
            feasible_withdrawal_amount = request.user.wallet.wallet_balance - reservation_amount

            if amount >= minimum_amount:
                if amount <= (feasible_withdrawal_amount):
                    user_wallet = Wallet.objects.get(user=request.user)
                    description = f'{account_name}/ {bank}'
                    create_order = Order.objects.create(
                        user=request.user,
                        transaction=f'Withdrawal request {transaction_id}',
                        amount=amount,
                        recipient=account_number,
                        description=description,
                        status='processing',
                        transaction_id=transaction_id
                    )

                    if create_order:
                        user_wallet.wallet_balance -= amount

                        user_wallet.save()
                        create_order.save()

                        messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')

                        return redirect('services:account_user_withdrawal')
                    else:
                        messages.warning(request, 'Sorry, your request could not be processed at the moment')

                        return redirect('services:account_user_withdrawal')
                else:
                    messages.warning(request, f'Not sufficient funds, you can only withdraw {feasible_withdrawal_amount} with your current balance')

                    return redirect('services:account_user_withdrawal')
            else:
                messages.warning(request, f'Least amount for Withdrawal is {minimum_amount}')

                return redirect('services:account_user_withdrawal')

    context = utils.dict_merge(
        external_context(),
        context,
        user_features(request.user.id),
        {
            'notice_notes': SiteSetting.objects.get(pk=1).withdrawal_note
        }
    )

    return render(request, template_name, context)


@login_required
def account_user_data(request):
    user_orders = [i for i in reversed(list(Order.objects.all()))]
    user_orders_truncate = [i for i in reversed(list(Order.objects.all()))][:5]

    api = API()

    networks = api.get_data_pricing()

    template_name = 'services/account_user_data.html'
    context = {
        'networks': networks,
        'user_orders': user_orders,
        'user_orders_truncate': user_orders_truncate,

    }

    if request.method == 'POST':
        data_form = DataForm(request.POST)
        if data_form.is_valid():
            product_code = data_form.cleaned_data.get('product_code')
            user_phone = data_form.cleaned_data.get('phone_number')
            amount = int(api.get_product(product_code)['price']) # from data_json
            network = api.get_product(product_code)['network'] # from data_json

            minimum_amount = SiteSetting.objects.get(pk=1).minimum_data
            reservation_amount = SiteSetting.objects.get(pk=1).reservation_amount
            data_charges = SiteSetting.objects.get(pk=1).data_charges
            amount -= data_charges
            feasible_withdrawal_amount = request.user.wallet.wallet_balance - reservation_amount

            if amount >= minimum_amount:
                if (feasible_withdrawal_amount) >= amount:
                    user_wallet = Wallet.objects.get(user=request.user)

                    transaction_id = api.make_transaction_id()

                    description = f'Data/{network} + charges (&#8358; {data_charges})'
                    create_order = Order.objects.create(
                        user=request.user,
                        transaction=f'Data purchase {transaction_id}',
                        amount=amount,
                        recipient=user_phone,
                        description=description,
                        transaction_id=transaction_id,
                        status='declined'
                    )

                    payload = {
                        'product_code': product_code,
                        'network': network,
                        'user_details': {
                            'phone_number': user_phone,
                            'transaction_id': transaction_id
                        }
                    }
                    api_request = api.buy_data(**payload)

                    if not api_request.get('code'):
                        if create_order:
                            user_wallet.wallet_balance -= amount
                            create_order.status = 'processed'
                            create_order.toggle_count = 1

                            user_wallet.save()
                            create_order.save()

                            messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')
                        else:
                            messages.warning(request, f'''Your order couldn't be placed at the moment :(''')
                    else:
                        messages.warning(request, 'Sorry, your request could not be processed at the moment')
                else:
                    messages.warning(request, f'Not sufficient funds, you can only use {feasible_withdrawal_amount} with your current balance')
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


@login_required
def account_user_airtime(request):
    user_orders = [i for i in reversed(list(Order.objects.all()))]
    user_orders_truncate = [i for i in reversed(list(Order.objects.all()))][:5]
    template_name = 'Home/account_user_airtime.html'

    context = {
        'networks': [i for i in Network.objects.order_by('-date')],
        'user_orders': user_orders,
        'user_orders_truncate': user_orders_truncate
    }

    if request.method == 'POST':
        airtime_form = AirtimeForm(request.POST)
        if airtime_form.is_valid():
            network = airtime_form.cleaned_data.get('network')
            user_phone = airtime_form.cleaned_data.get('phone_number')
            amount = airtime_form.cleaned_data.get('amount')

            minimum_amount = SiteSetting.objects.get(pk=1).minimum_airtime
            reservation_amount = SiteSetting.objects.get(pk=1).reservation_amount
            feasible_withdrawal_amount = request.user.wallet.wallet_balance - reservation_amount

            if amount >= minimum_amount:
                if (feasible_withdrawal_amount) >= amount:
                    user_wallet = Wallet.objects.get(user=request.user)

                    api = API()

                    transaction_id = api.make_transaction_id()

                    description = f'Airtime/{network}'
                    create_order = Order.objects.create(
                        user=request.user,
                        transaction=f'Airtime purchase {transaction_id}',
                        amount=amount,
                        recipient=user_phone,
                        description=description,
                        status='declined'
                    )

                    payload = {
                        'network': network,
                        'user_details': {
                            'phone_number': user_phone,
                            'transaction_id': transaction_id
                        },
                        'price': amount
                    }
                    api_request = api.buy_airtime(**payload)

                    if not api_request.get('code'):
                        if create_order:
                            create_order.status = 'processed'
                            create_order.toggle_count = 1

                            user_wallet.save()
                            create_order.save()

                            messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')
                        else:
                            messages.warning(request, f'''Your order couldn't be placed at the moment :(''')
                    else:
                        messages.warning(request, 'Sorry, your request could not be processed at the moment')
                else:
                    messages.warning(request, f'Not sufficient funds, you can only use {feasible_withdrawal_amount} with your current balance')
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


@login_required
@services_required
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


@login_required
@services_required
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


@login_required
@home_required
def adverts(request):
    template_name = 'Home/adverts.html'
    context = utils.dict_merge(
        external_context(),
        user_features(request.user.id)
    )

    advert_form = AdvertForm(request.POST, request.FILES)

    if request.method == 'POST':
        if advert_form.is_valid():
            advert_form.save()
        else:
            print(advert_form.errors)

    return render(request, template_name, context)


@login_required
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


@login_required
@home_required
def advert_delete(request, slug):
    advert = get_object_or_404(Advert, slug=slug)
    advert.delete()

    return redirect('services:adverts_list')
