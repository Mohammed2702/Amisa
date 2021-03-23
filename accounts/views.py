from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import datetime

from accounts.forms import (
	RegistrationForm,
	LoginForm,
	VerificationForm,
	ForgotPasswordForm,
	PasswordResetForm,
	ProfileForm,
    UserUpdateForm,
    PermissionsForm
)
from accounts.models import (
	PasswordReset
)
from codes.models import Code, CodeGroup
from Amisacb.utils import (
	dict_merge,
	generate_url_scrambled,
	generate_ver_code,
	deliver_mail,
)

from Amisacb.context import checker, external_context, user_features
from Amisacb import utils
from Amisacb.decorators import accounts_required

User = get_user_model()


def account_signup(request):
    date = datetime.datetime.now()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            user = authenticate(username=username, password=password)
            login(request, user)

            email_success = True

            context = {
                'reg_form': form,
                'user': request.user,
                'date': date,
                'email_success': email_success
            }

            context = dict_merge(external_context(), context)

            messages.info(request, 'Update your Profile to complete your registration')

            return redirect('accounts:account_profile')
    else:
        form = RegistrationForm()

    template_name = 'Home/account_signup.html'
    context = {
        'reg_form': form,
        'date': date,
    }

    context = dict_merge(external_context(), context)

    return render(request, template_name, context)


def account_signin(request):
    checker()

    form = LoginForm(request)
    if request.method == 'POST':
        if True:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)

                request.session.set_expiry(86400)

                return redirect('accounts:home')
            else:
                messages.error(request,'Username or Password not correct')

                return redirect('accounts:account_signin')
    else:
        form = LoginForm()

    template_name = 'Home/account_signin.html'
    context = {
        'form': form,
    }
    context = dict_merge(external_context(), context)

    return render(request, template_name, context)


def account_signout(request):
    logout(request)

    return redirect('accounts:account_signin')


def account_forgot_password(request):
    template_name = 'Home/account_forgot_password.html'
    context = {}

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')

            try:
                get_user = User.objects.get(username=username)
                get_user_email = get_user.email

                reset_link_navigator = generate_url_scrambled(list(PasswordReset.objects.all()))
                reset_link = f'{password_reset_main}/{reset_link_navigator}'
                verification_code = generate_ver_code()

                create_password_reset = PasswordReset.objects.create(
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
                    reset_link
                )
                recipient = get_user_email

                send_email = deliver_mail(
                    title=title,
                    body=body,
                    recipient=recipient
                )

                if send_email:
                    messages.info(request, f'Password reset link has been sent to your mail box.')

                    return redirect('accounts:account_forgot_password')
                else:
                    messages.info(request, f'Password reset link could not be sent please try again.')

                    return redirect('accounts:account_forgot_password')
            except Exception as e:
                print('account_password_reset', e)

                messages.info(request, 'Username does not exist.')

                return redirect('accounts:account_forgot_password')
    else:
        form = ForgotPasswordForm(request.POST)
    return render(request, template_name, context)


def account_forgot_password_link(request, link):
    from django.db import models as model

    checker()

    get_reset = PasswordReset.objects.get(link_slug=link)

    if request.method == 'POST':
        verification_form = VerificationForm(request.POST)
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

                            return redirect('accounts:home')
                    else:
                        messages.info(request, 'Password has reset Successfully')

                        return redirect('accounts:account_forgot_password_link', link=link)
                else:
                    messages.info(request, 'E-Mail or username is not valid.')

                    return redirect('accounts:account_forgot_password_link', link=link)
            else:
                messages.info(request, 'E-Mail or username is not valid.')

                return redirect('accounts:account_forgot_password_link', link=link)
    else:
        verification_form = VerificationForm(request.POST)

    template_name = 'accounts/account_reset_password.html'
    context = {}

    return render(request, template_name, context)


@login_required(login_url='accounts:account_signin')
def account_dashboard(request):
    if request.user.is_staff:
        all_code_groups = list(CodeGroup.objects.all())[-5:]
        all_codes = list(Code.objects.all())[-15:]
        context = {
            'user': request.user,
            'all_codes': all_codes,
            'all_code_groups': all_code_groups,
        }

        context = user_features(request.user.id)
        template_name = 'Home/account_dashboard.html'
        context = utils.dict_merge(external_context(), context)
    else:
        context = user_features(request.user.id)
        template_name = 'Home/account_user_dashboard.html'
        context = utils.dict_merge(external_context(), context)

    return render(request, template_name, context)


@accounts_required
@login_required(login_url='accounts:account_signin')
def account_users_wallet(request):
    template_name = 'Home/account_users_wallet.html'
    user_details = user_features(request.user.id)
    context = utils.dict_merge(external_context(), user_details)

    users = User.objects.order_by('-last_updated')
    context = utils.dict_merge(context, {'users': users})

    if request.method == 'POST':
        permission_form = PermissionsForm(request.POST)
        if permission_form.is_valid():
            username = permission_form.cleaned_data.get('username')
            home = permission_form.cleaned_data.get('home')
            blog = permission_form.cleaned_data.get('blog')
            services = permission_form.cleaned_data.get('services')
            codes = permission_form.cleaned_data.get('codes')
            account = permission_form.cleaned_data.get('account')

            get_user = User.objects.get(username=username)
            get_user.is_home = home
            get_user.is_blog = blog
            get_user.is_services = services
            get_user.is_codes = codes
            get_user.is_account = account

            get_user.save()

            message = f'Permissions for {username} was updated'
            messages.info(request, message)
        # else:
        #     print(permission_form.errors)
    else:
        permission_form = PermissionsForm()

    return render(request, template_name, context)


# Profile


@login_required(login_url='accounts:account_signin')
def account_profile(request):
    template_name = 'Home/account_profile.html'
    user_details = user_features(request.user.id)

    profile_form = ProfileForm(instance=request.user.profile)
    user_update_form = UserUpdateForm(instance=request.user)
    password_reset_form = PasswordResetForm(request.POST)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        user_update_form = UserUpdateForm(request.POST, instance=request.user)
        password_reset_form = PasswordResetForm(request.POST)

        if profile_form.is_valid():
            profile_form.save()

            new_state = profile_form.cleaned_data.get('state')
            new_phone_number = profile_form.cleaned_data.get('phone_number')

            profile_user = User.objects.get(pk=request.user.id)

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

            return redirect('accounts:account_profile')
        else:
            profile_form = ProfileForm(instance=request.user)

        if user_update_form.is_valid():
            get_user = User.objects.select_for_update().filter(pk=request.user.id)

            username = user_update_form.cleaned_data.get('username')
            password = request.POST.get('password1')
            authenticate_user = authenticate(username=username, password=password)

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

                return redirect('accounts:account_profile')
            else:
                pass
        else:
            user_update_form = UserUpdateForm(instance=request.user)

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

            return redirect('accounts:account_profile')
        else:
            password_reset_form = ProfileForm(instance=request.user)
    
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


@accounts_required
@login_required(login_url='accounts:account_signin')
def toggle_permission(request, username):
    try:
        if request.user.is_superuser:
            user = User.objects.get(username=username)
            if user.is_staff:
                user.is_staff = False
            elif not user.is_staff:
                user.is_staff = True

            user.save()
            return redirect('accounts:account_users_wallet')
        else:
            return render(request, 'Home/404Error.html')
    except User.DoesNotExist:
        return render(request, 'Home/404Error.html')
