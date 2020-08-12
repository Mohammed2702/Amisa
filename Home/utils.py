from django.core.mail import send_mail
from django.utils import timezone
from Amisacb import settings
import string
import random
import datetime


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


# Reloadly

import requests


# Operators ...

airtime = {
	'airtel': 342,
	'mtn': 341,
	'glo': 344,
	'9mobile': 340
}

data = {
	'airtel': 646,
	'mtn': 345,
	'glo': 647,
	'9mobile': 645
}


def get_token():
	url = "https://auth.reloadly.com/oauth/token"
	payload = {
		"client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "grant_type": "client_credentials",
        "audience": settings.CLIENT_LIVE
	}

	headers = {
	  'Content-Type': 'application/json',
	  'Accept': 'application/json'
	}

	data = requests.post(url, json=payload, headers=headers)

	return data

    
def get_balance():
	auth_token=get_token()

	if auth_token:
		auth_token = auth_token.json()['access_token']
		url = f'{settings.CLIENT_LIVE}/accounts/balance'
		headers = {
		  'Accept': 'application/com.reloadly.topups-v1+json',
		  'Authorization': f'Bearer {auth_token}'
		}

		data = requests.get(url, headers=headers)

		return data.json()['balance']
	else:
		return False


def get_discount_all():
	auth_token=get_token()

	if auth_token:
		auth_token = auth_token.json()['access_token']
		url = f'{settings.CLIENT_LIVE}/operators/commissions'
		headers = {
		  'Accept': 'application/com.reloadly.topups-v1+json',
		  'Authorization': f'Bearer {auth_token}'
		}

		data = requests.get(url, headers=headers)

		return data.json()
	else:
		return False


def get_discount_by_id(countryID=646):
	auth_token=get_token()

	if auth_token:
		auth_token = auth_token.json()['access_token']
		url = f'{settings.CLIENT_LIVE}/operators/{countryID}/commissions'
		headers = {
		  'Accept': 'application/com.reloadly.topups-v1+json',
		  'Authorization': f'Bearer {auth_token}'
		}

		data = requests.get(url, headers=headers)

		return data.json()
	else:
		return False


def get_fx_by_id(ID=646, amount=100):
	auth_token=get_token()

	if auth_token:
		auth_token = auth_token.json()['access_token']
		url = f'{settings.CLIENT_LIVE}/operators/fx-rate'
		headers = {
		  'Content-Type': 'application/json',
		  'Accept': 'application/com.reloadly.topups-v1+json',
		  'Authorization': f'Bearer {auth_token}'
		}

		data = {
			"operatorId": ID,
  			"amount": amount
		}

		data = requests.post(url, headers=headers, json=data)

		return data.json()
	else:
		return False


def get_countries():
	auth_token=get_token()

	if auth_token:
		auth_token = auth_token.json()['access_token']
		url = f'{settings.CLIENT_LIVE}/countries'
		headers = {
		  'Accept': 'application/com.reloadly.topups-v1+json',
		}

		data = requests.get(url, headers=headers)

		return data.json()
	else:
		return False


def get_country_by_iso(iso):
	auth_token=get_token()

	if auth_token:
		auth_token = auth_token.json()['access_token']
		url = f'{settings.CLIENT_LIVE}/countries/{iso}'
		headers = {
		  'Accept': 'application/com.reloadly.topups-v1+json',
		}

		data = requests.get(url, headers=headers)

		return data.json()
	else:
		return False


def make_topup(ops_ID, amount, recipient, sender='', customIdentifier=''):
	auth_token=get_token()

	if auth_token:
		auth_token = auth_token.json()['access_token']
		url = f'{settings.CLIENT_LIVE}/topups'
		headers = {
			'Content-Type': 'application/json',
		  	'Accept': 'application/com.reloadly.topups-v1+json',
		  	'Authorization': f'Bearer {auth_token}'
		}

		r_countryCode = 'NG'
		s_countryCode = 'NG'

		value = {
			"recipientPhone": {
				"countryCode": r_countryCode,
				"number": recipient
			},
			"senderPhone": {
				"countryCode": s_countryCode,
				"number": sender
			},
			"operatorId": ops_ID,
			"amount": amount,
			"customIdentifier": customIdentifier
		}

		data = requests.post(url, headers=headers, json=value)

		return data.json()
	else:
		return False
