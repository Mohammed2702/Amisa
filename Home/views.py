from django.shortcuts import *
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import *
from django.contrib.auth import *
from django.http import JsonResponse
from django.contrib.auth.decorators import *
from django.contrib import messages
from django.utils import timezone
import random
import datetime
import time
import os


from . import forms
from . import models
from . import utils


# ENV

password_reset_main = 'amisacb.pythonanywhere.com/forgot_password'

if os.path.isdir('/home/mohammed/Desktop/Projects/Amisa/Amisacb/Home/'):
	message_dir = '/home/mohammed/Desktop/Projects/Amisa/Amisacb/Home/'
else:
	message_dir = '/home/Amisacb/GitProject/Home/'


# External contexts


def checker():
    curr_date = str(datetime.datetime.now()).split(' ')[0].split('-')
    curr_time = str(datetime.datetime.now()).split(' ')[1].split(':')
    curr_exp_date = datetime.date(int(curr_date[0]), int(curr_date[1]), int(curr_date[2]))
    curr_order_date = datetime.datetime(
        int(curr_date[0]),
        int(curr_date[1]),
        int(curr_date[2]),
        int(curr_time[0]),
        int(curr_time[1]),
        10
    )

    all_orders = models.Order.objects.all()
    for i in all_orders:
        order = models.Order.objects.get(pk=i.id)
        order_expiry_date = str(order.expiry_date).split(' ')
        order_expiry_date = datetime.datetime(
            int(order_expiry_date[0].split('-')[0]),
            int(order_expiry_date[0].split('-')[1]),
            int(order_expiry_date[0].split('-')[2]),
            int(order_expiry_date[1].split(':')[0]),
            int(order_expiry_date[1].split(':')[1]),
            10
        )

        if curr_order_date >= order_expiry_date:
            description = ' - Order was Declined.'
            if description not in order.description:
                order.description += description
                order.status = 'Declined'
                wallet = models.Wallet.objects.get(user=order.user)
                wallet.wallet_balance += order.amount
                wallet.save()

        order.save()

    all_codes = models.Code.objects.all()
    for i in all_codes:
        code = models.Code.objects.get(pk=i.id)
        if code.code_group.status:
            code.status = True
        else:
            code.status = False

        code_date_ = str(code.expiry_date).split(' ')[0].split('-')
        code_exp_date = datetime.date(int(code_date_[0]), int(code_date_[1]), int(code_date_[2]))
        if code_exp_date <= curr_exp_date:
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

    all_resets = models.PasswordReset.objects.all()

    for i in all_resets:
        reset = models.PasswordReset.objects.get(pk=i.id)
        reset_expiry_date = str(reset.expiry_date).split(' ')
        reset_expiry_date = datetime.datetime(
            int(reset_expiry_date[0].split('-')[0]),
            int(reset_expiry_date[0].split('-')[1]),
            int(reset_expiry_date[0].split('-')[2]),
            int(reset_expiry_date[1].split(':')[0]),
            int(reset_expiry_date[1].split(':')[1]),
            10
        )

        if curr_order_date >= reset_expiry_date:
            reset.delete()


def external_context():
    checker()

    external_context = {
        'year': time.gmtime().tm_year,
        'total_amount': sum([i['wallet_balance'] for i in list(models.Wallet.objects.all().values('wallet_balance'))]),
        'all_codes_count': len(list(models.Code.objects.all())),
        'all_agents': len(list(models.Profile.objects.filter(account_type='Agent'))),
        'all_customers': len(list(models.Profile.objects.filter(account_type='User'))),
        'all_codes': [i for i in reversed(models.Code.objects.all())],
        'code_groups': [i for i in reversed(list(models.CodeGroup.objects.all()))],
        'notice_notes': models.SiteSetting.objects.get(pk=1).services_note,
        'all_networks': models.Network.objects.all(),
        'get_settings': models.SiteSetting.objects.get(pk=1),
        'resolutions': models.Resolution.objects.all(),
    }

    return external_context


# Get user details


def user_features(user_id):
    checker()

    user = get_object_or_404(User, pk=user_id)
    user_profile = models.Profile.objects.get(user=user)
    user_wallet = models.Wallet.objects.get(user=user)
    all_states = models.user_location
    all_states = [i[1] for i in all_states]
    all_account_types = models.account_types
    all_account_types = [i[1] for i in all_account_types]
    user_history = [i for i in reversed(list(models.History.objects.all().filter(user=user)))]
    user_history_truncate = [i for i in reversed(list(models.History.objects.all().filter(user=user)))][:10]
    posts = [i for i in reversed(list(models.Post.objects.all()))][:5]

    # Orders

    if user.is_superuser:
        orders = [i for i in reversed(list(models.Order.objects.all()))][:5]

        notifications = orders + posts
    else:
        orders = [i for i in reversed(list(models.Order.objects.all().filter(user=user)))][:5]

        notifications = orders + posts

    context = {
        'current_user': user,
        'user_profile': user_profile,
        'user_wallet': user_wallet,
        'all_states': all_states,
        'all_account_types': all_account_types,
        'user_history': user_history,
        'user_history_truncate': user_history_truncate,
        'notifications': notifications,
        'orders': orders,
        'posts': posts,
        'notifications_count': len(notifications),
    }

    return context


# Errors


def custom_404(request, exception=None):
    return render(request, template_name='Home/404Error.html')


def custom_500(request, exception=None):
    return render(request, template_name='Home/500Error.html')


def custom_403(request, exception=None):
    return render(request, template_name='Home/403Error.html')


def custom_400(request, exception=None):
    return render(request, template_name='Home/400Error.html')


# AUTHs


def account_signup(request):
    try:
        checker()

        date = datetime.datetime.now()
        if request.method == 'POST':
            form = forms.RegistrationForm(request.POST)
            if form.is_valid():
                form.save()

                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')

                user = authenticate(username=username, password=password)
                login(request, user)

                existing_ids = list(models.Profile.objects.values_list('reference_id'))

                new_reference_id = utils.generate_referrence_id(existing_ids)

                profile_model = models.Profile.objects.create(
                    user=user,
                    reference_id=new_reference_id,
                    account_type='User',
                )
                profile_model.save()

                wallet_model = models.Wallet.objects.create(
                    user=user,
                    wallet_balance=0.0
                )
                wallet_model.save()

                title = 'Registration Successfull'
                body = open(f'{message_dir}/registration_message.txt', 'r').read().format(
                    request.user.get_full_name(),
                    request.user.username,
                    request.user.email,
                    request.user.profile.account_type,
                    request.user.profile.reference_id
                )
                recipient = request.user.email

                email_success = utils.deliver_mail(
                    title=title,
                    body=body,
                    recipient=recipient
                )

                context = {
                    'reg_form': form,
                    'user': request.user,
                    'date': date,
                    'email_success': email_success
                }

                print(f'E-Mail for {request.user.profile.reference_id} returned {email_success}')
                context = utils.dict_merge(external_context(), context)

                messages.info(request, 'Update your Profile to complete your registration')

                return redirect('Home:account_profile')
        else:
            form = forms.RegistrationForm()

        template_name = 'Home/account_signup.html'
        context = {
            'reg_form': form,
            'date': date,
        }

        context = utils.dict_merge(external_context(), context)

        return render(request, template_name, context)
    except Exception as e:
        print('account_signup', e)


def account_signin(request):
    try:
        checker()

        form = AuthenticationForm(request)
        if request.method == 'POST':
            if True:
                username = request.POST['username']
                password = request.POST['password']

                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)

                    request.session.set_expiry(86400)

                    return redirect('Home:home')
                else:
                    messages.error(request,'Username or Password not correct')

                    return redirect('Home:account_signin')
        else:
            form = AuthenticationForm()

        template_name = 'Home/account_signin.html'
        context = {
            'form': form,
        }
        context = utils.dict_merge(external_context(), context)

        return render(request, template_name, context)
    except Exception as e:
        print('account_signin', e)


def account_signout(request):
    try:
        checker()

        logout(request)

        return redirect('Home:account_signin')
    except Exception as e:
        print('account_signout', e)


def account_forgot_password(request):
    try:
        checker()

        template_name = 'Home/account_forgot_password.html'
        context = {}

        if request.method == 'POST':
            form = forms.ForgotPasswordForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')

                try:
                    get_user = User.objects.get(username=username)
                    get_user_email = get_user.email

                    reset_link_navigator = utils.generate_url_scrambled(list(models.PasswordReset.objects.all()))
                    reset_link = f'{password_reset_main}/{reset_link_navigator}'
                    verification_code = utils.generate_ver_code()

                    create_password_reset = models.PasswordReset.objects.create(
                        user=get_user,
                        link_slug=reset_link_navigator,
                        verification_code=verification_code
                    )
                    create_password_reset.save()

                    title = 'Password Reset'
                    body = open(f'{message_dir}password_retrieved.txt', 'r').read().format(
                        get_user.username,
                        get_user.get_full_name(),
                        get_user.username,
                        get_user.email,
                        get_user.profile.account_type,
                        reset_link
                    )
                    recipient = get_user_email

                    send_email = utils.deliver_mail(
                        title=title,
                        body=body,
                        recipient=recipient
                    )

                    if send_email:
                        messages.info(request, f'Password reset link has been sent to your mail box.')

                        return redirect('Home:account_forgot_password')
                    else:
                        messages.info(request, f'Password reset link could not be sent please try again.')

                        return redirect('Home:account_forgot_password')
                except Exception as e:
                    print('account_password_reset', e)

                    messages.info(request, 'Username does not exist.')

                    return redirect('Home:account_forgot_password')
        else:
            form = forms.ForgotPasswordForm(request.POST)
        return render(request, template_name, context)
    except Exception as e:
        print('account_password_reset', e)


def account_forgot_password_link(request, link):
    from django.db import models as model
    try:
        checker()

        get_reset = models.PasswordReset.objects.get(link_slug=link)

        if request.method == 'POST':
            verification_form = forms.VerificationForm(request.POST)
            if verification_form.is_valid():
                username = verification_form.cleaned_data.get('username')
                email = verification_form.cleaned_data.get('email')
                new_password = verification_form.cleaned_data.get('new_password')
                confirm_password = verification_form.cleaned_data.get('confirm_password')

                if get_reset.user.username == username:
                    if get_reset.user.email == email:
                        if new_password == confirm_password:
                            user = User.objects.get(username=get_reset.user.username)
                            user.set_password(new_password)
                            user.save()

                            messages.info(request, 'Password has been reset Successfully')

                            user = authenticate(username=get_reset.user.username, password=new_password)

                            if user:
                                login(request, user)

                                return redirect('Home:home')
                        else:
                            messages.info(request, 'Password has reset Successfully')

                            return redirect('Home:account_forgot_password_link', link=link)
                    else:
                        messages.info(request, 'E-Mail or username is not valid.')

                        return redirect('Home:account_forgot_password_link', link=link)
                else:
                    messages.info(request, 'E-Mail or username is not valid.')

                    return redirect('Home:account_forgot_password_link', link=link)
        else:
            verification_form = forms.VerificationForm(request.POST)

        template_name = 'Home/account_reset_password.html'
        context = {}

        return render(request, template_name, context)
    except model.DoesNotExist:
        messages.info(request, 'Your link has expired. Request for another reset link.')

        return redirect('Home:account_forgot_password')
    except Exception as e:
        print('account_forgot_password_link', e)


# Dashboard


@login_required(login_url='Home:account_signin')
def account_dashboard(request):
    try:
        if request.user.is_superuser:
            all_code_groups = list(models.CodeGroup.objects.all())[-5:]
            all_codes = list(models.Code.objects.all())[-15:]
            context = {
                'user': request.user,
                'all_codes': all_codes,
                'all_code_groups': all_code_groups,
            }

            context = user_features(request.user.id)
            context = utils.dict_merge(context, context)
            context = utils.dict_merge(external_context(), context)
            template_name = 'Home/account_dashboard.html'

            return render(request, template_name, context)
        else:
            context = user_features(request.user.id)
            context = utils.dict_merge(external_context(), context)
            template_name = 'Home/account_user_dashboard.html'

            return render(request, template_name, context)
    except Exception as e:
        print('account_dashboard', e)


@login_required(login_url='Home:account_signin')
def account_users_list(request, user_type):
    try:
        if user_type == 'customers':
            user_type = True
            users = models.Profile.objects.all().filter(account_type='User')
        else:
            user_type = False
            users = models.Profile.objects.all().filter(account_type='Agent')

        template_name = 'Home/account_users_list.html'
        user_details = user_features(request.user.id)
        context = utils.dict_merge(external_context(), user_details)
        context = utils.dict_merge(
            context, {'user_type': user_type, 'users': users})

        return render(request, template_name, context)
    except Exception as e:
        print('account_users_list', e)


@login_required(login_url='Home:account_signin')
def account_users_wallet(request):
    try:
        template_name = 'Home/account_users_wallet.html'
        user_details = user_features(request.user.id)
        context = utils.dict_merge(external_context(), user_details)

        if request.user.is_superuser:
            users = User.objects.all()
            context = utils.dict_merge(context, {'users': users})

            return render(request, template_name, context)
        else:
            context = {
                'users': User.objects.all().filter(id=request.user.id)
            }
            context = utils.dict_merge(external_context(), context)

            return render(request, template_name, context)
    except Exception as e:
        print('account_users_wallet', e)


# Profile


@login_required(login_url='Home:account_signin')
def account_profile(request):
    try:
        template_name = 'Home/account_profile.html'
        user_details = user_features(request.user.id)

        profile_form = forms.ProfileForm(instance=request.user.profile)
        user_update_form = forms.UserUpdateForm(instance=request.user)
        password_reset_form = forms.PasswordResetForm(request.POST)

        if request.method == 'POST':
            profile_form = forms.ProfileForm(request.POST, instance=request.user.profile)
            user_update_form = forms.UserUpdateForm(request.POST, instance=request.user)
            password_reset_form = forms.PasswordResetForm(request.POST)

            if profile_form.is_valid():
                profile_form.save()

                new_account_type = profile_form.cleaned_data.get(
                    'account_type')
                new_state = profile_form.cleaned_data.get('state')
                new_phone_number = profile_form.cleaned_data.get('phone_number')

                profile_user = User.objects.get(pk=request.user.id)

                profile_user.profile.account_type = new_account_type
                profile_user.profile.state = new_state
                profile_user.profile.phone_number = new_phone_number

                profile_user.save()

                title = 'Profile Update'
                body = open(f'{message_dir}/change_in_login_details.txt', 'r').read().format(
                    request.user.first_name,
                    request.user.get_full_name(),
                    request.user.username,
                    request.user.email,
                    request.user.profile.account_type,
                    request.user.profile.reference_id
                )
                recipient = request.user.email

                email_success = utils.deliver_mail(
                    title=title,
                    body=body,
                    recipient=recipient
                )

                print(f'E-Mail for {request.user.profile.reference_id} returned {email_success}')

                if email_success:
                    messages.info(request, 'Your profile is now up to date :)')
                else:
                    messages.info(request, 'Your profile could not be set, sorry ... :(')

                return redirect('Home:account_profile')
            else:
                profile_form = forms.ProfileForm(instance=request.user)

            if user_update_form.is_valid():
                get_user = User.objects.select_for_update().filter(pk=request.user.id)

                username = user_update_form.cleaned_data.get('username')
                password = request.POST.get('password1')
                authenticate_user = authenticate(
                    username=username, password=password)

                if authenticate_user:
                    first_name = user_update_form.cleaned_data.get(
                        'first_name')
                    last_name = user_update_form.cleaned_data.get('last_name')
                    email = user_update_form.cleaned_data.get('email')

                    user_update_form.save()

                    title = 'Profile Update'
                    body = open(f'{message_dir}/change_in_login_details.txt', 'r')
                    body = body.read().format(
                        request.user.first_name,
                        request.user.get_full_name(),
                        request.user.username,
                        request.user.email,
                        request.user.profile.account_type,
                        request.user.profile.reference_id
                    )
                    recipient = email

                    email_success = utils.deliver_mail(
                        title=title,
                        body=body,
                        recipient=recipient
                    )

                    print(f'E-Mail for {request.user.profile.reference_id} returned {email_success}')

                    if email_success:
                        messages.info(request, 'Your profile is now up to date :)')
                    else:
                        messages.info(request, 'Your profile could not be set, sorry ... :(')

                    return redirect('Home:account_profile')
                else:
                    pass
            else:
                user_update_form = forms.UserUpdateForm(instance=request.user)

            if password_reset_form.is_valid():
                user = User.objects.get(pk=request.user.id)

                old_password = password_reset_form.cleaned_data.get('old_password')
                new_password = password_reset_form.cleaned_data.get('new_password')
                confirm_password = password_reset_form.cleaned_data.get('confirm_password')

                authenticate_user = authenticate(username=request.user.username, password=old_password)

                if new_password == confirm_password:
                    if authenticate_user:
                        user.set_password(new_password)
                        title = 'Password Reset'
                        body = open(f'{message_dir}/change_in_login_details.txt', 'r').read().format(
                            request.user.first_name,
                            request.user.get_full_name(),
                            request.user.username,
                            request.user.email,
                            request.user.profile.account_type,
                            request.user.profile.reference_id
                        )
                        recipient = request.user.email

                        email_success = utils.deliver_mail(
                            title=title,
                            body=body,
                            recipient=recipient
                        )

                        print(f'E-Mail for {request.user.profile.reference_id} returned {email_success}')

                        if email_success:
                            messages.info(request, 'Password reset Successfull, check your E-Mail for verfication')
                        else:
                            messages.info(request, 'Password reset could not be done, E-Mail could not be sent :(')
                        user.save()
                    else:
                        messages.info(request, 'Incorrect password, try again')
                else:
                    messages.info(request, 'Password mismatch')

                return redirect('Home:account_profile')
            else:
                password_reset_form = forms.ProfileForm(instance=request.user)

        context = utils.dict_merge(
            user_details,
            {
                'profile_form': profile_form,
                'user_update_form': user_update_form,
                'password_reset_form': password_reset_form
            }
        )
        context = utils.dict_merge(external_context(), context)

        return render(request, template_name, context)
    except Exception as e:
        print('account_profile', e)


# Code


@login_required
def account_code(request):
    try:
        code_redeem_form = forms.CodeRedeemForm(request.POST)
        if request.user.is_superuser:
            template_name = 'Home/account_code.html'
            context = utils.dict_merge(
                external_context(), user_features(request.user.id))
        else:
            context = {}
            if request.user.profile.account_type == 'User':
                rate = models.SiteSetting.objects.get(pk=1).agent_rate
            else:
                rate = models.SiteSetting.objects.get(pk=1).customer_rate

            rate /= 100

            template_name = 'Home/account_user_code.html'
            if request.method == 'POST':
                if code_redeem_form.is_valid():
                    code_redeem = code_redeem_form.cleaned_data.get('code')
                    context = {'code_redeem': code_redeem}

                    try:
                        user_code = models.Code.objects.get(code=code_redeem)
                        print(f'Code {code_redeem} {user_code.code} {user_code.status}')
                        if user_code.code_group.status:
                            code_amount = user_code.amount
                            description = 'Code Redemption'
                            if user_code.status:
                                user_wallet = models.Wallet.objects.get(user=request.user)
                                code_recharge = code_amount - (rate * code_amount)
                                user_wallet.wallet_balance += code_recharge
                                user_wallet.save()

                                log_history = models.History.objects.create(
                                    user=request.user,
                                    description=description,
                                    amount=code_amount,
                                    charges=rate,
                                    status=True
                                )

                                log_history.save()

                                user_code.code += '/Used'
                                user_code.status = False

                                user_code.save()

                                messages.info(
                                    request,
                                    f'{code_redeem} has been redeemed\
                                    successfully, your new Wallet Balance is\
                                     {request.user.wallet.wallet_balance}'
                                    )

                                return redirect('Home:account_code')
                            else:
                                messages.info(request, f'{code_redeem} has expired')

                                return redirect('Home:account_code')
                        else:
                            messages.info(request, f'{code_redeem} has been disabled')

                            return redirect('Home:account_code')
                    except models.Code.DoesNotExist:
                        messages.info(request, f'{code_redeem} does not exist')

                        return redirect('Home:account_code')
                    except Exception as e:
                        print(f'account_code {e}')
            else:
                code_redeem_form = forms.CodeRedeemForm()

            context = utils.dict_merge(context, {'code_redeem_form': code_redeem_form})
            context = utils.dict_merge(external_context(), context)
            context = utils.dict_merge(context, user_features(request.user.id))

        return render(request, template_name, context)
    except Exception as e:
        print('account_code', e)


@login_required
def account_code_group(request, action_type, group_id):
    try:
        if request.user.is_superuser:
            code_group = models.CodeGroup.objects.get(pk=group_id)
            if action_type == 'delete':
                code_group.delete()

                return redirect('Home:home')
            else:
                if code_group.status:
                    code_group.status = False
                    code_group.save()

                    return redirect('Home:home')
                else:
                    code_group.status = True
                    code_group.save()

                    return redirect('Home:home')
        else:
            return render(request, 'Home/404Error.html')
    except Exception as e:
        print('account_code_group', e)


@login_required(login_url='Home:account_signin')
def account_code_details(request, code_id):
    try:
        if request.user.is_active:
            if request.user.is_superuser:
                template_name = 'Home/account_code_details.html'
                context = {
                    'code': get_object_or_404(models.Code, pk=code_id)
                }

                context = utils.dict_merge(external_context(), context)

                return render(request, template_name, context)
            else:
                return redirect('Home:home')
        else:
            template_name = 'Home/404Error.html'
            context = {
                'code': get_object_or_404(models.Code, pk=code_id)
            }

            context = utils.dict_merge(external_context(), context)

            return render(request, template_name, context)
    except Exception as e:
        print('account_code_details', e)


@login_required(login_url='Home:account_signin')
def account_code_delete(request, code_id):
    try:
        if request.user.is_active:
            if request.user.is_superuser:
                code = models.Code.objects.get(pk=code_id)
                code.delete()
                # code.save()

                return redirect('Home:account_code')
            else:
                code = models.Code.objects.get(pk=code_id)

                if request.user.id == code_slip.user.id:
                    code.delete()

                    return redirect('Home:account_code')
                else:
                    logout(request)

                    return redirect('Home:account_signin')
        else:
            template_name = 'Home/404Error.html'
            context = {}

            context = utils.dict_merge(external_context(), context)

            return render(request, template_name, context)
    except Exception as e:
        print('account_code_delete', e)


@login_required(login_url='Home:account_signin')
def account_code_toggle(request, code_id):
    try:
        if request.user.is_superuser:
            code = models.Code.objects.get(pk=code_id)
            if code.status:
                description = 'Order was Declined by Admin.'
                code.status = False

                log_history = models.History.objects.create(
                    user=request.user,
                    description=description,
                    amount=code.amount,
                    charges=str(code.status),
                )
            else:
                description = 'Order was Approved by Admin.'
                code.status = True

                log_history = models.History.objects.create(
                    user=request.user,
                    description=description,
                    amount=code.amount,
                    charges=str(code.status),
                )

            code.save()
            log_history.save()

            return redirect('Home:account_code')
        else:
            template_name = 'Home/404Error.html'
            context = {}

            context = utils.dict_merge(external_context(), context)

            return render(request, template_name, context)
    except Exception as e:
        print('account_code_toggle', e)


@login_required(login_url='Home:account_signin')
def account_code_request(request):
    try:
        template_name = 'Home/account_code_requests.html'
        context = {}
        if request.user.is_active:
            if request.user.is_superuser:
                all_code_groups = list(models.CodeGroup.objects.all())[-5:]
                current_date = str(datetime.datetime.now())
                all_codes = models.Code.objects.all()
                code_value = utils.generate_code(all_codes.values('code'))

                code_group_form = forms.CodeGroupForm()
                code_form = forms.CodeForm()

                context = {
                    'all_code_groups': all_code_groups,
                    'all_codes': all_codes,
                    'code_form': code_form,
                    'code_group_form': code_group_form,
                    'code_value': code_value,
                    'current_date': current_date,
                }
                context = utils.dict_merge(external_context(), context)

                if request.method == 'POST':
                    code_group_form = forms.CodeGroupForm(request.POST)
                    code_form = forms.CodeForm(request.POST)

                    if code_form.is_valid():
                        code_group = code_form.cleaned_data.get('code_group')
                        code_group = models.CodeGroup.objects.get(
                            id=code_group)
                        code = code_form.cleaned_data.get('code')
                        amount = code_form.cleaned_data.get('amount')
                        date_ = str(code_form.cleaned_data.get(
                            'expiry_date')).replace('/', '-').split(' ')[0]
                        date_ = date_.split('-')
                        year = date_[2]
                        day = date_[1]
                        month = date_[0]
                        expiry_date = f'{year}-{month}-{day}'

                        create_code = models.Code.objects.create(
                            code_group=code_group,
                            code=code,
                            amount=amount,
                            expiry_date=expiry_date
                        )

                        create_code.save()

                        return redirect('Home:account_code')
                    else:
                        code_form = forms.CodeForm()

                    if code_group_form.is_valid():
                        code_group_name = code_group_form.cleaned_data['code_group_name']
                        create_code_group = models.CodeGroup.objects.create(
                            code_group_name=code_group_name
                        )

                        create_code_group.save()

                        return redirect('Home:account_code_request')
                    else:
                        code_group_form = forms.CodeGroupForm()

                    context = {
                        'all_code_groups': all_code_groups,
                        'all_codes': all_codes,
                        'code_form': code_form,
                        'code_group_form': code_group_form,
                        'code_value': code_value,
                        'current_date': current_date,
                    }

                    context = utils.dict_merge(external_context(), context)

                    return render(request, template_name, context)
            else:
                return redirect('Home:home')
        else:
            return redirect('Home:home')

        return render(request, template_name, context)
    except Exception as e:
        print('account_code_request', e)


# Services

@login_required(login_url='Home:account_signin')
def account_user_withdrawal(request):
    try:
        user_orders = [i for i in reversed(list(models.Order.objects.all()))]
        user_orders_truncate = [i for i in reversed(
            list(models.Order.objects.all()))][:5]

        context = {
            'banks': utils.get_all_banks(),
            'user_orders': user_orders,
            'user_orders_truncate': user_orders_truncate,

        }
        template_name = 'Home/account_user_withdrawal.html'

        if request.method == 'POST':
            try:
                withdrawal_form = forms.WithdrawalForm(request.POST)
                if withdrawal_form.is_valid():
                    account_number = withdrawal_form.cleaned_data.get(
                        'account_number')
                    account_name = withdrawal_form.cleaned_data.get(
                        'account_name')
                    bank = withdrawal_form.cleaned_data.get('bank')
                    amount = withdrawal_form.cleaned_data.get('amount')

                    minimum_amount = models.SiteSetting.objects.get(pk=1).minimum_withdrawal

                    if amount >= minimum_amount:
                        if amount <= request.user.wallet.wallet_balance:
                            user_wallet = models.Wallet.objects.get(
                                user=request.user)
                            user_wallet.wallet_balance -= amount

                            request.session['amount_error'] = False

                            create_order = models.Order.objects.create(
                                user=request.user,
                                transaction='Withdrawal request',
                                amount=amount,
                                recipient=account_number,
                                description=f'{account_name}/ {bank}'
                            )

                            if create_order:
                                order_mail = utils.deliver_mail_order(
                                    title='',
                                    body=create_order.desc()
                                )

                                if order_mail:
                                    user_wallet.save()
                                    create_order.save()

                                    messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')
                                else:
                                    create_order.delete()

                                    messages.warning(request, f'''Your order couldn't be placed at the moment :(''')

                                return redirect('Home:account_user_withdrawal')
                            else:
                                messages.warning(request, 'Sorry, your request could not be processed at the moment')

                                return redirect('Home:account_user_withdrawal')
                        else:
                            messages.warning(request, 'Not sufficient funds')

                            return redirect('Home:account_user_withdrawal')
                    else:
                        messages.warning(request, f'Least amount for Withdrawal is {minimum_amount}')

                        return redirect('Home:account_user_withdrawal')
            except Exception as e:
                print('User Withdrawal', e)

        context = utils.dict_merge(external_context(), context)
        context = utils.dict_merge(context, user_features(request.user.id))

        return render(request, template_name, context)
    except Exception as e:
        print('account_user_withdrawal', e)


@login_required(login_url='Home:account_signin')
def account_user_data(request):
    try:
        user_orders = [i for i in reversed(list(models.Order.objects.all()))]
        user_orders_truncate = [i for i in reversed(list(models.Order.objects.all()))][:5]

        template_name = 'Home/account_user_data.html'
        context = {
            'networks': [i.network for i in list(models.Network.objects.all())],
            'user_orders': user_orders,
            'user_orders_truncate': user_orders_truncate,

        }

        if request.method == 'POST':
            data_form = forms.DataForm(request.POST)
            if data_form.is_valid():
                network = data_form.cleaned_data.get('network')
                user_phone = data_form.cleaned_data.get('phone_number')
                amount = data_form.cleaned_data.get('amount')

                minimum_amount = models.SiteSetting.objects.get(pk=1).minimum_data

                if amount >= minimum_amount:
                    if request.user.wallet.wallet_balance >= amount:
                        user_wallet = models.Wallet.objects.get(user=request.user)
                        user_wallet.wallet_balance -= amount

                        create_order = models.Order.objects.create(
                            user=request.user,
                            transaction='Data purchase request',
                            amount=amount,
                            recipient=user_phone,
                            description=f'Data/{network}'
                        )

                        if create_order:
                            order_mail = utils.deliver_mail_order(
                                title='',
                                body=create_order.desc()
                            )
                            if order_mail:
                                user_wallet.save()
                                create_order.save()

                                messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')
                            else:
                                create_order.delete()

                                messages.warning(request, f'''Your order couldn't be placed at the moment :(''')

                            return redirect('Home:account_user_data')
                        else:
                            messages.warning(request, 'Sorry, your request could not be processed at the moment')

                            return redirect('Home:account_user_data')
                    else:
                        messages.warning(request, 'Not sufficient funds')

                        return redirect('Home:account_user_data')
                else:
                    messages.warning(request, f'Least amount for Data is {minimum_amount}')

                    return redirect('Home:account_user_data')

        context = utils.dict_merge(external_context(), context)
        context = utils.dict_merge(context, user_features(request.user.id))

        return render(request, template_name, context)
    except Exception as e:
        print('account_user_data', e)


@login_required(login_url='Home:account_signin')
def account_user_airtime(request):
    try:
        user_orders = [i for i in reversed(list(models.Order.objects.all()))]
        user_orders_truncate = [i for i in reversed(list(models.Order.objects.all()))][:5]
        template_name = 'Home/account_user_airtime.html'
        context = {
            'networks': [i.network for i in list(models.Network.objects.all())],
            'user_orders': user_orders,
            'user_orders_truncate': user_orders_truncate,

        }

        if request.method == 'POST':
            data_form = forms.DataForm(request.POST)
            if data_form.is_valid():
                network = data_form.cleaned_data.get('network')
                user_phone = data_form.cleaned_data.get('phone_number')
                amount = data_form.cleaned_data.get('amount')

                minimum_amount = models.SiteSetting.objects.get(pk=1).minimum_airtime

                if amount >= minimum_amount:
                    if request.user.wallet.wallet_balance >= amount:
                        user_wallet = models.Wallet.objects.get(user=request.user)
                        user_wallet.wallet_balance -= amount

                        create_order = models.Order.objects.create(
                            user=request.user,
                            transaction='Airtime purchase request',
                            amount=amount,
                            recipient=user_phone,
                            description=f'Airtime/{network}'
                        )

                        if create_order:
                            order_mail = utils.deliver_mail_order(
                                title='',
                                body=create_order.desc()
                            )

                            if order_mail:
                                user_wallet.save()
                                create_order.save()

                                messages.warning(request, f'''Your order has been placed, keep checking your notifications to track your order(s) :)''')
                            else:
                                create_order.delete()

                                messages.warning(request, f'''Your order couldn't be placed at the moment :(''')

                            return redirect('Home:account_user_airtime')
                        else:
                            messages.warning(request, 'Sorry, your request could not be processed at the moment')

                            return redirect('Home:account_user_airtime')
                    else:
                        messages.warning(request, 'Not sufficient funds')

                        return redirect('Home:account_user_airtime')
                else:
                    messages.warning(request, f'Least amount for Airtime is {minimum_amount}')

                    return redirect('Home:account_user_airtime')

        context = utils.dict_merge(external_context(), context)
        context = utils.dict_merge(context, user_features(request.user.id))

        return render(request, template_name, context)
    except Exception as e:
        print('account_user_airtime', e)


# Tools


@login_required(login_url='Home:account_signin')
def code_group_codes(request, group_id):
    try:
        if request.user.is_superuser:
            template_name = 'Home/code_group_codes.html'

            group = models.CodeGroup.objects.get(pk=group_id)
            code_group_children = list(models.Code.objects.all().filter(code_group=group))

            init_context = {
                'group': group,
                'code_group_children': code_group_children,
            }
            context = utils.dict_merge(external_context(), user_features(request.user.id))
            context = utils.dict_merge(init_context, context)

            return render(request, template_name, context)
        else:
            return render(request, 'Home/404Error.html')
    except Exception as e:
        print('code_group_codes', e)


@login_required(login_url='Home:account_signin')
def site_settings(request):
    try:
        if request.user.is_superuser:
            get_setting = models.SiteSetting.objects.get(pk=1)
            if request.method == 'POST':
                settings_form = forms.SiteSettingForm(request.POST)
                network_form = forms.NetworkForm(request.POST)

                if network_form.is_valid():
                    network = network_form.cleaned_data.get('network')
                    data_rate = network_form.cleaned_data.get('data_rate')

                    if network not in [i.network for i in models.Network.objects.all()]:
                        create_network = models.Network.objects.create(
                            network=network,
                            data_rate=data_rate,
                        )

                        if create_network:
                            create_network.save()

                            messages.warning(request, f'{network} has been added to networks')

                            return redirect('Home:site_settings')
                        else:
                            messages.warning(request, f'{network} could not be added')

                            return redirect('Home:site_settings')
                    else:
                        messages.warning(request, f'{network} already exist !!!')

                        return redirect('Home:site_settings')

                elif settings_form.is_valid():
                    customer_rate = settings_form.cleaned_data.get('customer_rate')
                    agent_rate = settings_form.cleaned_data.get('agent_rate')
                    services_note = settings_form.cleaned_data.get('services_note')
                    minimum_withdrawal = settings_form.cleaned_data.get('minimum_withdrawal')
                    minimum_airtime = settings_form.cleaned_data.get('minimum_airtime')
                    minimum_data = settings_form.cleaned_data.get('minimum_data')
                    call_contact = settings_form.cleaned_data.get('call_contact')
                    whatsapp_contact = settings_form.cleaned_data.get('whatsapp_contact')
                    email_contact = settings_form.cleaned_data.get('email_contact')
                    how_to = settings_form.cleaned_data.get('how_to')
                    about_us = settings_form.cleaned_data.get('about_us')

                    get_setting.customer_rate = customer_rate
                    get_setting.agent_rate = agent_rate
                    get_setting.services_note = services_note
                    get_setting.minimum_withdrawal = minimum_withdrawal
                    get_setting.minimum_airtime = minimum_airtime
                    get_setting.minimum_data = minimum_data
                    get_setting.call_contact = call_contact
                    get_setting.whatsapp_contact = whatsapp_contact
                    get_setting.email_contact = email_contact
                    get_setting.how_to = how_to
                    get_setting.about_us = about_us

                    get_setting.save()

                    messages.warning(request, 'Settings Update Successful !!!')

                    return redirect('Home:site_settings')
            else:
                settings_form = forms.SiteSettingForm(request.POST)
                network_form = forms.NetworkForm(request.POST)

            template_name = 'Home/site_settings.html'
            context = utils.dict_merge(external_context(), user_features(request.user.id))
            context = utils.dict_merge(context, {'settings_form': settings_form, 'get_setting': get_setting})

            return render(request, template_name, context)
        else:
            return render(request, 'Home/404Error.html')
    except Exception as e:
        print('site_settings', e)


@login_required(login_url='Home:account_signin')
def show_all_orders(request):
    try:
        template_name = 'Home/show_all_orders.html'
        context = utils.dict_merge(external_context(), user_features(request.user.id))

        user_orders = [i for i in reversed(list(models.Order.objects.all().filter(user=request.user)))]
        user_orders_truncate = [i for i in reversed(list(models.Order.objects.all().filter(user=request.user))[:5])]
        admin_orders = [i for i in reversed(list(models.Order.objects.all()))]
        admin_orders_truncate = [i for i in reversed(list(models.Order.objects.all()))][:5]

        user_context = {
            'networks': [i.network for i in list(models.Network.objects.all())],
            'user_orders': user_orders,
            'user_orders_truncate': user_orders_truncate,
            'admin_orders': admin_orders,
            'admin_orders_truncate': admin_orders_truncate,

        }
        context = utils.dict_merge(context, user_context)

        return render(request, template_name, context)
    except Exception as e:
        print('show_all_orders', e)


@login_required(login_url='Home:account_signin')
def toggle_order(request, order_id):
    try:
        if request.user.is_superuser:
            order = models.Order.objects.get(pk=order_id)

            order.status = 'Approved'
            order_message = open(f'{message_dir}/accept_order.txt', 'r').read().format(
                request.user.get_full_name,
                request.user.profile.reference_id,
                order.description
            )

            title = 'Order Approved'
            body = order_message
            recipient = request.user.email

            email_success = utils.deliver_mail(
                title=title,
                body=body,
                recipient=recipient
            )
            
            print(f'E-Mail send returns {email_success} for {request.user.email}')

            if order:
                order.save()

                return redirect('Home:home')
            else:
                return redirect('Home:show_all_orders')
        else:
            template_name = 'Home/404Error.html'
            return render(request, template_name)
    except Exception as e:
        print('toggle_order', e)


def all_posts(request):
    try:
        get_all_posts = [i for i in reversed(list(models.Post.objects.all()))]

        user_context = {
            'all_posts': get_all_posts,

        }
        context = utils.dict_merge(
            user_context, user_features(request.user.id))

        template_name = 'Home/posts.html'

        if request.method == 'POST':
            if request.user.is_superuser:
                post_form = forms.PostForm(request.POST)
                context = utils.dict_merge(context, {'post_form': post_form})
                if post_form.is_valid():
                    post_title = post_form.cleaned_data.get('post_title')
                    post_content = post_form.cleaned_data.get('post_content')

                    create_post = models.Post.objects.create(
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
            post_form = forms.PostForm()
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


@login_required(login_url='Home:account_signin')
def post_edit(request, post_id):
    try:
        pass
    except Exception as e:
        print('post_edit', e)


@login_required(login_url='Home:account_signin')
def post_delete(request, post_id):
    try:
        if request.user.is_superuser:
            post = models.Post.objects.get(pk=post_id)
            post.delete()

            messages.info(request, 'Post was successfully deleted :)')

            return redirect('Home:posts')
        else:
            return render(request, 'Home/404Error.html')
    except models.Post.DoesNotExist:
        return render(request, 'Home/404Error.html')
    except Exception as e:
        print('post_delete', e)


# Extras


def charges_and_pricing(request):
    try:
        if str(request.user) != 'AnonymousUser':
            user_orders = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user)))]
            user_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user))[:5])]
            admin_orders = [i for i in reversed(
                list(models.Order.objects.all()))]
            admin_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all()))][:5]

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
    try:
        if str(request.user) != 'AnonymousUser':
            print(type(request.user), 'True')
            user_orders = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user)))]
            user_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user))[:5])]
            admin_orders = [i for i in reversed(
                list(models.Order.objects.all()))]
            admin_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all()))][:5]

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
    except Exception as e:
        print('terms_of_use', e)


def card_issuance(request):
    try:
        if str(request.user) != 'AnonymousUser':
            user_orders = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user)))]
            user_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user))[:5])]
            admin_orders = [i for i in reversed(
                list(models.Order.objects.all()))]
            admin_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all()))][:5]

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

            template_name = 'Home/card_issuance.html'

            return render(request, template_name, context)
        else:
            user_context = {
            }
            context = user_context

            template_name = 'Home/card_issuance.html'

            return render(request, template_name, context)
    except Exception as e:
        print('card_issuance', e)


def how_to(request):
    try:
        if str(request.user) != 'AnonymousUser':
            user_orders = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user)))]
            user_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user))[:5])]
            admin_orders = [i for i in reversed(
                list(models.Order.objects.all()))]
            admin_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all()))][:5]

            user_context = {
                'user_orders': user_orders,
                'user_orders_truncate': user_orders_truncate,
                'admin_orders': admin_orders,
                'admin_orders_truncate': admin_orders_truncate,
                'get_setting': models.SiteSetting.objects.get(pk=1),

            }
            context = user_context
            context = utils.dict_merge(external_context(), context)

            user_details = utils.dict_merge(
                user_features(request.user.id), context)
            context = utils.dict_merge(external_context(), user_details)

            template_name = 'Home/how_to.html'

            return render(request, template_name, context)
        else:
            user_context = {
                'get_setting': models.SiteSetting.objects.get(pk=1),
            }
            context = user_context

            template_name = 'Home/how_to.html'

            return render(request, template_name, context)
    except Exception as e:
        print('card_issuance', e)


def faq(request):
    try:
        if str(request.user) != 'AnonymousUser':
            user_orders = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user)))]
            user_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all().filter(user=request.user))[:5])]
            admin_orders = [i for i in reversed(
                list(models.Order.objects.all()))]
            admin_orders_truncate = [i for i in reversed(
                list(models.Order.objects.all()))][:5]

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
            user_details = user_features(request.user.id)
            context = utils.dict_merge(external_context(), user_details)

            template_name = 'Home/faq.html'

            return render(request, template_name, context)
        else:
            user_context = {
            }
            context = user_context
            context = utils.dict_merge(external_context(), context)

            template_name = 'Home/faq.html'

            return render(request, template_name, context)
    except Exception as e:
        print('card_issuance', e)


@login_required(login_url='Home:account_signin')
def resolution(request):
    try:
        user_context = {}
        context = utils.dict_merge(
            user_context,
            user_features(request.user.id)
        )

        template_name = 'Home/resolution.html'

        context = utils.dict_merge(external_context(), context)

        resolution_form = forms.ResolutionForm(request.POST)
        reply_form = forms.ReplyForm(request.POST)
            
        if request.method == 'POST':
            resolution_form = forms.ResolutionForm(request.POST)
            reply_form = forms.ReplyForm(request.POST)

            context = utils.dict_merge(context, {
                'resolution_form': resolution_form,
                'reply_form': reply_form
                })
            if resolution_form.is_valid():
                resolution_content = resolution_form.cleaned_data.get('resolution_content')

                create_resolution = models.Resolution.objects.create(
                    author=request.user,
                    content=resolution_content,
                )

                if create_resolution:
                    create_resolution.save()

                    messages.info(request, 'Your request has been sent, we\'ll get back to you')

                    return redirect('Home:resolution')
                else:
                    messages.info(request, 'Sorry, your request could not be processed, please try again')

                    return redirect('Home:resolution')

            if reply_form.is_valid():
                reply_content = reply_form.cleaned_data.get('reply_content')
                post_id = reply_form.cleaned_data.get('post')
                create_reply = models.Reply.objects.create(
                    author=request.user,
                    post=models.Resolution.objects.get(pk=post_id),
                    content=reply_content,
                )

                if create_reply:
                    create_reply.save()

                    messages.info(request, 'Your reply has been sent :)')

                    return redirect('Home:resolution')
                else:
                    messages.info(request, 'Sorry, your request could not be processed, please try again')

                    return redirect('Home:resolution')
        else:
            resolution_form = forms.ResolutionForm()
            reply_form = forms.ReplyForm()

            context = utils.dict_merge(
                context,
                {
                    'resolution_form': resolution_form,
                    'reply_form': reply_form
                }
            )

        return render(request, template_name, context)
    except Exception as e:
        print('resolution', e)


@login_required(login_url='Home:account_signin')
def resolution_details(request, resolution_id):
    try:
        resolution = models.Resolution.objects.get(pk=id)

        user_context = {
            'resolution': resolution
        }
        context = utils.dict_merge(
            user_context,
            user_features(request.user.id)
        )

        template_name = 'Home/resolution_details.html'

        context = utils.dict_merge(external_context(), context)

        return render(request, template_name, context)
    except Exception as e:
        print('resolution_details', e)
