from django.core.mail import send_mail
from Amisacb import settings
import string
import random
import secrets


code_limit = 5
signs = [
    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+',
    '-', '=', '\\', '//', '`', '|'
]
numbers = [i for i in range(0, 9)]
alphabets_lower = [i for i in string.ascii_lowercase]
alphabets_upper = [i for i in string.ascii_uppercase]

all_keys = numbers + alphabets_lower + alphabets_upper

UNWANTED_REF_SIGNS = ['-', '_']
REFERENCE_ID_MAX_LENGTH = 7

def comma_sep(value):
    value_usage = []
    value = str(value)

    if len(value) > 3:
        for i in value:
            value_usage.append(i)
        for i in range(1, len(value), 3):
            value_usage.insert(i, ',')
        value_usage_str = '100000'
        print(value_usage)
        for i in value_usage:
            value_usage_str += str(i)
        value = value_usage_str
    else:
        value = str(value)

    return value


def generate_code(existing_codes):
    code = f'{random.choice(all_keys)}{random.choice(all_keys)}{random.choice(all_keys)}-{random.choice(all_keys)}{random.choice(all_keys)}{random.choice(all_keys)}-{random.choice(all_keys)}{random.choice(all_keys)}{random.choice(all_keys)}-{random.choice(all_keys)}{random.choice(all_keys)}{random.choice(all_keys)}'
    while code not in existing_codes:
        break
    else:
        code = f'{random.choice(all_keys)}{random.choice(all_keys)}{random.choice(all_keys)}-{random.choice(all_keys)}{random.choice(all_keys)}{random.choice(all_keys)}-{random.choice(all_keys)}{random.choice(all_keys)}{random.choice(all_keys)}-{random.choice(all_keys)}{random.choice(all_keys)}{random.choice(all_keys)}'

    return code.upper()


def generate_referrence_id(existing_ids):
    ref = secrets.token_urlsafe(REFERENCE_ID_MAX_LENGTH)

    while ref in existing_ids:
        ref = secrets.token_urlsafe(REFERENCE_ID_MAX_LENGTH)

    for i in UNWANTED_REF_SIGNS:
        if i in ref:
            ref = ref.replace(i, '0')

    ref = ref.upper()

    return ref


def dict_merge(*dictionaries):
    dictionary = {}

    for d in dictionaries:
        dictionary = {
            **dictionary,
            **d
        }

    return dictionary


def deliver_mail(title, body, recipient):
    mail_delivery = send_mail(
        title,
        body,
        recipient,
        [recipient],
        fail_silently=True
    )

    if mail_delivery == 1:
        return True
    else:
        if settings.DEBUG:
            return True
        else:
            return False


def deliver_mail_order(title='Amisa order', body='Hey there, you got a test E-Mail', recipient=settings.ADMIN_EMAIL):
    body = f'{body[i] for i in range(len(body))}'
    
    mail_delivery = send_mail(
        title,
        body,
        recipient,
        [recipient],
        fail_silently=True
    )
    
    if mail_delivery == 1:
        return True
    else:
        if settings.DEBUG:
            return True
        else:
            return False


all_chars = alphabets_lower + alphabets_upper + numbers


def generate_url_scrambled(existing_url_scrambled):
    url_scrambled = f'{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}'
    while url_scrambled not in existing_url_scrambled:
        break
    else:
        url_scrambled = f'{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}'

    return url_scrambled


def generate_ver_code():
    return random.randint(10000, 99999)
