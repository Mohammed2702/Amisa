from django.utils import timezone
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


User = get_user_model()


def checker():
    curr_date = timezone.now().date()
    curr_time = timezone.now().time()
    curr_exp_date = curr_date
    curr_order_date = timezone.now()

    all_orders = Order.objects.filter(status='processing')
    for i in all_orders:
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

    all_codes = Code.objects.all()
    for i in all_codes:
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

    all_resets = PasswordReset.objects.all()

    for i in all_resets:
        reset = PasswordReset.objects.get(pk=i.id)
        if reset.is_expired():
            reset.delete()


def external_context():
    checker()

    external_context = {
        'year': time.gmtime().tm_year,
        'total_amount': sum([i['wallet_balance'] for i in list(Wallet.objects.all().values('wallet_balance'))]),
        'all_codes_count': len(list(Code.objects.all())),
        'all_customers': len(list(Profile.objects.order_by('-date_joined'))),
        'all_codes': [i for i in reversed(Code.objects.all())],
        'code_groups': [i for i in reversed(list(CodeGroup.objects.all()))],
        'notice_notes': SiteSetting.objects.get_or_create(pk=1)[0].services_note,
        'all_networks': Network.objects.all(),
        'get_settings': SiteSetting.objects.get_or_create(pk=1)[0],
        'all_banks': Bank.objects.all(),
        'locations': Locator.objects.all(),
        'adverts': Advert.objects.order_by('-priority')
    }

    return external_context


# Get user details


def user_features(user_id):
    checker()

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
