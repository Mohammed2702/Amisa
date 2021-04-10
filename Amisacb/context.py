from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from services.models import (
    Order,
    Bank,
    Network,
    Locator,
    Advert
)
from home.models import (
    SiteSetting,
    History
)
from codes.models import (
    Code,
    CodeGroup
)
from accounts.models import (
    Profile,
    Wallet,
    PasswordReset
)
from Amisacb.data import user_location

import time
import concurrent.futures as cf


User = get_user_model()


def check_orders():
    orders = Order.objects.filter(status='processing')
    for i in orders:
        order = Order.objects.get(slug=i.slug)

        if order.is_expired():
            description = ' - Order was Declined.'
            if description not in order.description:
                order.description += description
                order.status = 'declined'
                wallet = Wallet.objects.get(user=order.user)
                wallet.wallet_balance += order.amount
                wallet.save()

        order.save()


def check_codes():
    codes = Code.objects.all()
    for i in codes:
        code = Code.objects.get(slug=i.slug)
        if code.code_group.status:
            code.status = True
        else:
            code.status = False

        if code.is_expired():
            if 'Expired' not in str(code.code).split('/'):
                code.code = f'{code.code}/Expired'
            code.status = False
        else:
            if 'Expired' in str(code.code).split('/'):
                code.code = f'{code.code}'.replace('/Expired', '')
            code.status = True

        if 'Used' in str(code.code).split('/'):
            code.code = f'{code.code}'
            code.status = False

        code.save()


def check_password_resets(passwords):
    all_resets = PasswordReset.objects.all()

    for i in all_resets:
        reset = PasswordReset.objects.get(pk=i.id)
        if reset.is_expired():
            reset.delete()


def checker():
    with cf.ProcessPoolExecutor() as executor:
        executor.submit(check_orders)
        executor.submit(check_codes)
        executor.submit(check_password_resets)


def get_total_amount():
    wallet_balance = Wallet.objects.values_list('wallet_balance', flat=True)
    amount = sum(wallet_balance)
    return amount


def external_context():
    checker()

    external_context = {
        'year': time.gmtime().tm_year,
        'total_amount': get_total_amount(),
        'all_codes_count': len(list(Code.objects.all())),
        'all_customers': len(list(Profile.objects.order_by('-date_joined'))),
        'all_codes': Code.objects.order_by('-date_created'),
        'code_groups': CodeGroup.objects.order_by('-date_created'),
        'all_networks': Network.objects.order_by('-date'),
        'get_settings': SiteSetting.objects.get_or_create(pk=1)[0],
        'all_banks': Bank.objects.order_by('-date'),
        'locations': Locator.objects.order_by('-date'),
        'adverts': Advert.objects.order_by('-priority')
    }

    return external_context


# Get user details


def user_features(user_id):
    user = get_object_or_404(User, pk=user_id)
    user_profile = Profile.objects.get(user=user)
    user_wallet = Wallet.objects.get(user=user)
    all_states = user_location
    all_states = [i[1] for i in all_states]
    user_history = [i for i in reversed(list(History.objects.all().filter(user=user)))]
    user_history_truncate = [i for i in reversed(list(History.objects.all().filter(user=user)))][:10]

    # Orders

    if user.is_staff:
        orders = [i for i in reversed(list(Order.objects.all()))][:5]
    else:
        orders = [i for i in reversed(list(Order.objects.all().filter(user=user)))][:5]

    context = {
        'current_user': user,
        'user_profile': user_profile,
        'user_wallet': user_wallet,
        'all_states': all_states,
        'user_history': user_history,
        'user_history_truncate': user_history_truncate,
        'orders': orders,
    }

    return context
