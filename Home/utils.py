from django.core.mail import send_mail
from django.utils import timezone
from Amisacb import settings
import string
import random
import datetime
import re
from django.template.defaultfilters import slugify


def unique_slugify(
	instance,
	value,
	slug_field_name='slug',
	queryset=None,
	slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value


code_limit = 5
signs = [
	'!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+',
		'-', '=', '\\', '//', '`', '|'
	]
numbers = [i for i in range(0, 9)]
alphabets_lower = [i for i in string.ascii_lowercase]
alphabets_upper = [i for i in string.ascii_uppercase]

all_keys = numbers + alphabets_lower + alphabets_upper


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

	return code


def generate_referrence_id(existing_ids):
	ref = f'{random.choice(alphabets_upper)}{random.choice(alphabets_upper)}{random.choice(alphabets_upper)}-{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}'
	while ref not in existing_ids:
		break
	else:
		ref = f'{random.choice(alphabets_upper)}{random.choice(alphabets_upper)}{random.choice(alphabets_upper)}-{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}{random.choice(numbers)}'

	return ref


def dict_merge(dict1, dict2):
	return {**dict1, **dict2}


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
