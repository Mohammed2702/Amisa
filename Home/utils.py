from django.core.mail import send_mail
from django.utils import timezone
from Amisacb import settings
import string
import random
import datetime
# import africastalking


# class SMS:
#     def __init__(self, sender, recipients, message):
#         # Set Credentials here

#         self.sender = sender
#         self.recipients = recipients
#         self.message = message
#         self.username = "sandbox"
#         self.api_key = "b83c915d9678cf6a8cafc2a2525f052e23f25c93d5c2a881cf26ce7569f095b7"

#         # Initialize the SDK
#         africastalking.initialize(self.username, self.api_key)

#         # Get the SMS service
#         self.sms = africastalking.SMS

#     def send(self):
#             # Set the numbers you want to send to in international format
#             recipients = self.recipients

#             # Set your message
#             message = self.message

#             # Set your shortCode or senderId
#             sender = self.sender
#             try:
# 				# Thats it, hit send and we'll take care of the rest.
#                 response = self.sms.send(message, recipients, sender)
#                 return(response)
#             except Exception as e:
#                 return('Encountered an error while sending: %s' % str(e))


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
    print(body)
    if mail_delivery == 1:
        return True
    else:
        return False


def get_all_banks():
	banks = ['Access Bank', 'First Bank', 'UBA', 'GT-Bank']
	return banks


def check_date(date):
	date = str(date).split('-')
	current_date = str(datetime.datetime.now()).split(' ')[0].split('-')

	year = int(date[0])
	month = int(date[1])
	day = int(date[2])

	current_year = int(current_date[0])
	current_month = int(current_date[1])
	current_day = int(current_date[2])

	if year <= current_year:
	    if month <= current_month:
	        if day < current_day:
	            return True
	        else:
	            return False
	    else:
	        False
	else:
		return False


def default_time():
	now = str(datetime.datetime.now()).split(' ')[1]
	return now

all_chars = alphabets_lower + alphabets_upper + numbers


def generate_url_scrambled(existing_url_scrambled):
	url_scrambled = f'{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}'
	while url_scrambled not in existing_url_scrambled:
		break
	else:
		url_scrambled = f'{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}{random.choice(all_chars)}'

	return url_scrambled


def generate_ver_code():
	return random.randint(10000, 99999)


def order_expiry(order_range=3):
	date = str(datetime.datetime.now()).split(' ')[0].split('-')
	time = str(datetime.datetime.now()).split(' ')[1].split(':')
	current_year = int(date[0])
	current_month = int(date[1])
	current_day = int(date[2])
	current_hour = int(time[0]) + order_range
	current_minute = int(time[1])
	current_seconds = int(time[2].split('.')[0])

	if current_hour > 23:
		current_hour = 0
		current_day += 1

	return current_year, current_month, current_day, current_hour, current_minute, current_seconds


def password_expiry(order_range=5):
	date = str(datetime.datetime.now()).split(' ')[0].split('-')
	time = str(datetime.datetime.now()).split(' ')[1].split(':')
	current_year = int(date[0])
	current_month = int(date[1])
	current_day = int(date[2])
	current_hour = int(time[0])
	current_minute = int(time[1]) + order_range
	current_seconds = int(time[2].split('.')[0])

	if current_minute > 59:
		current_minute = 0
		current_hour += 1

	return current_year, current_month, current_day, current_hour, current_minute, current_seconds
