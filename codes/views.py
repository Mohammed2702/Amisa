from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.http import HttpResponse

from weasyprint import HTML
import datetime

from Amisacb import utils
from Amisacb.context import user_features, external_context
from codes.forms import CodeRedeemForm, CodeGroupForm
from codes.models import CodeGroup, Code
from accounts.models import Wallet
from home.models import (
    SiteSetting,
    History
)
from Amisacb.decorators import codes_required


@login_required
def account_code(request):
    template_name = 'Home/account_user_code.html'
    code_redeem_form = CodeRedeemForm(request.POST)
    if request.user.is_staff:
        template_name = 'Home/account_code.html'
        context = utils.dict_merge(
            external_context(),
            user_features(request.user.id)
        )
    else:
        context = {}
        rate = SiteSetting.objects.get(pk=1).customer_rate

        rate /= 100

        if request.method == 'POST':
            if code_redeem_form.is_valid():
                code_redeem = code_redeem_form.cleaned_data.get('code')
                context = {'code_redeem': code_redeem}

                try:
                    user_code = Code.objects.get(code=code_redeem)
                    if user_code.code_group.status:
                        code_amount = user_code.amount
                        description = 'Code Redemption'
                        if user_code.status:
                            user_wallet = Wallet.objects.get(user=request.user)
                            code_recharge = code_amount - (rate * code_amount)
                            user_wallet.wallet_balance += code_recharge

                            log_history = History.objects.create(
                                user=request.user,
                                description=description,
                                amount=code_amount,
                                charges=rate,
                                status=True
                            )

                            log_history.save()

                            user_code.code += '/Used'
                            user_code.used_by = str(request.user.username)
                            user_code.status = False

                            user_code.save()
                            user_wallet.save()

                            messages.info(
                                request,
                                f'{code_redeem} has been redeemed\
                                successfully, your new Wallet Balance is\
                                 {request.user.wallet.wallet_balance}'
                            )

                            return redirect('codes:account_code')
                        else:
                            messages.info(request, f'{code_redeem} has expired')

                            return redirect('codes:account_code')
                    else:
                        messages.info(request, f'{code_redeem} has been disabled')

                        return redirect('codes:account_code')
                except Code.DoesNotExist:
                    messages.info(request, f'{code_redeem} does not exist or has been used')

            return redirect('codes:account_code')
        else:
            code_redeem_form = CodeRedeemForm()

        context = utils.dict_merge(
            context,
            {'code_redeem_form': code_redeem_form},
            external_context(),
            user_features(request.user.id)
        )

    return render(request, template_name, context)


@login_required
@codes_required
def account_code_group(request, action_type, group_slug):
    if request.user.is_staff:
        code_group = CodeGroup.objects.get(slug=group_slug)
        if action_type == 'delete':
            code_group.delete()

            return redirect('accounts:home')
        else:
            if code_group.status:
                code_group.status = False
            else:
                code_group.status = True

            code_group.save()
            return redirect('accounts:home')
    else:
        return render(request, 'Home/404Error.html')


@login_required
def account_code_details(request, code_slug):
    if request.user.is_active:
        if request.user.is_staff:
            template_name = 'Home/account_code_details.html'
            context = {
                'code': get_object_or_404(Code, slug=code_slug)
            }

            context = utils.dict_merge(external_context(), context)

            return render(request, template_name, context)
        else:
            return redirect('accounts:home')
    else:
        template_name = 'Home/404Error.html'
        context = {
            'code': get_object_or_404(Code, slug=code_slug)
        }

        context = utils.dict_merge(external_context(), context)

        return render(request, template_name, context)


@login_required
@codes_required
def account_code_delete(request, code_slug):
    if request.user.is_active:
        if request.user.is_staff:
            code = Code.objects.get(slug=code_slug)
            code.delete()

            return redirect('codes:account_code')
        else:
            code = Code.objects.get(slug=code_slug)

            if request.user.id == code_slip.user.id:
                code.delete()

                return redirect('codes:account_code')
            else:
                logout(request)

                return redirect('Home:account_signin')
    else:
        template_name = 'Home/404Error.html'
        context = {}

        context = utils.dict_merge(external_context(), context)

        return render(request, template_name, context)


@login_required
@codes_required
def account_code_toggle(request, code_slug):
    code = Code.objects.get(slug=code_slug)

    if code.status:
        description = 'Order was Declined by Admin.'
        code.status = False
    else:
        description = 'Order was Approved by Admin.'
        code.status = True

    log_history = History.objects.create(
        user=request.user,
        description=description,
        amount=code.amount,
        charges=str(code.status),
    )
    code.save()
    log_history.save()

    return redirect('codes:account_code')


@login_required
@codes_required
def account_code_request(request):
    template_name = 'Home/account_code_requests.html'
    context = {}

    if request.user.is_staff:
        all_code_groups = list(CodeGroup.objects.all())[-5:]
        current_date = str(datetime.datetime.now())
        all_codes = Code.objects.all()
        code_value = utils.generate_code(all_codes.values('code'))

        if request.method == 'POST':
            code_group_form = CodeGroupForm(request.POST)

            if code_group_form.is_valid():
                code_group_data = code_group_form.cleaned_data
                code_batch_number = code_group_data.get('code_batch_number')

                create_code_group = CodeGroup.objects.create(
                    code_batch_number=code_batch_number
                )
                create_code_group.save()

                create_code_group.create_codes(**code_group_data)
            else:
                for error in code_group_form.errors.values():
                    messages.info(request, error)

            return redirect('codes:account_code_request')
        else:
            code_group_form = CodeGroupForm()

        context = {
            'all_code_groups': all_code_groups,
            'all_codes': all_codes,
            'code_group_form': code_group_form,
            'code_value': code_value
        }

        context = utils.dict_merge(external_context(), context)
    else:
        return redirect('accounts:home') # redirect to 404

    return render(request, template_name, context)


def html_to_pdf_view(request, page):
    code_batch = get_object_or_404(CodeGroup, slug=page)
    codes = Code.objects.filter(code_group=code_batch)

    context = {
        'code_batch': code_batch,
        'codes': codes
    }

    html_string = render_to_string('Home/code-batch-sheet.html', context)
    filename = f'{code_batch.code_batch_number}.pdf'
    html = HTML(string=html_string)
    html.write_pdf(target=f'/tmp/{filename}');

    fs = FileSystemStorage('/tmp')
    with fs.open(filename) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    return response


@login_required
@codes_required
def code_batch_sheet(request, slug):
    code_batch = get_object_or_404(CodeGroup, slug=slug)
    code = Code.objects.filter(code_group=code_batch)

    template_name = 'Home/code-batch-sheet.html'
    context = {
        'code_batch': code_batch,
        'codes': code
    }
    context = utils.dict_merge(
        external_context(),
        context
    )

    return render(request, template_name, context)


@login_required
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
