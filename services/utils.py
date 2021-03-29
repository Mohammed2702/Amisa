from django.conf import settings
from django.shortcuts import reverse

import json
import requests
import os
import random

from services.models import Order


class API:
    CONFIG_FILE = os.path.join(settings.BASE_DIR, 'config.json')
    DATA_CONFIG_FILE = os.path.join(
        settings.BASE_DIR,
        'services/data_config.json'
    )

    DATA_ENDPOINT = 'https://mobilenig.com/API/data?\
    username={0}\
    &api_key={1}\
    &network={2}\
    &phoneNumber={3}\
    &product_code{4}\
    &price={5}\
    &trans_id={6}\
    &return_url={7}'
    DATA_QUERY_ENDPOINT = 'https://mobilenig.com/API/data_query?\
    username={0}\
    &api_key={1}\
    &trans_id={2}'

    AIRTIME_ENDPOINT = 'https://mobilenig.com/API/airtime?\
    username={0}\
    &api_key={1}\
    &network={2}\
    &phoneNumber={3}\
    &amount={4}\
    &trans_id={5}'
    AIRTIME_QUERY_ENDPOINT = 'https://mobilenig.com/API/airtime_query?\
    username={0}\
    &api_key={1}\
    &trans_id={2}'

    with open(CONFIG_FILE, 'r') as CONFIG:
        CONFIG = json.load(CONFIG)

    with open(DATA_CONFIG_FILE, 'r') as DATA_CONFIG:
        DATA_CONFIG = json.load(DATA_CONFIG)

    API_KEY = CONFIG['API_KEY']
    API_USERNAME = CONFIG['API_USERNAME']

    def buy_data(self, product_code, network, user_details):
        product = self.DATA_CONFIG[network.lower()][product_code]
        phone_number = user_details['phone_number']
        price = product['price']
        network = network.upper()
        transaction_id = user_details['transaction_id']

        payload = {}

        payload['network'] = network
        payload['phone_number'] = phone_number
        payload['product_code'] = product_code
        payload['price'] = price
        payload['transaction_id'] = transaction_id

        endpoint = self.format_data_endpoint(**payload)
        response = requests.get(url=endpoint)
        response = response.json()

        if response.get('code'):
            print(f'{response}')

        return response

    def buy_airtime(self, network, user_details, price):
        phone_number = user_details['phone_number']
        transaction_id = user_details['transaction_id']
        network = network.upper()

        payload = {}

        payload['network'] = network
        payload['phone_number'] = phone_number
        payload['price'] = price
        payload['transaction_id'] = transaction_id

        endpoint = self.format_airtime_endpoint(**payload)
        response = requests.get(url=endpoint)
        response = response.json()

        if response.get('code'):
            print(f'{response}')

        return response

    def get_airtime_transaction(self, transaction_id):
        endpoint = self.format_airtime_query_endoint(transaction_id)
        response = requests.get(endpoint)
        response = response.json()

        return response

    def get_data_transaction(self, transaction_id):
        endpoint = self.format_data_query_endoint(transaction_id)
        response = requests.get(endpoint)
        response = response.json()

        return response

    def format_data_endpoint(self, **kwargs):
        username = self.API_USERNAME
        api_key = self.API_KEY
        network = kwargs['network']
        phone_number = kwargs['phone_number']
        product_code = kwargs['product_code']
        price = kwargs['price']
        trans_id = kwargs['transaction_id']
        return_url = reverse('services:account_user_data')

        endpoint = self.DATA_ENDPOINT.format(
            username,
            api_key,
            network,
            phone_number,
            product_code,
            price,
            trans_id,
            return_url
        ).replace('  ', '')

        return endpoint

    def format_data_query_endoint(self, transaction_id):
        username = self.API_USERNAME
        api_key = self.API_KEY
        trans_id = transaction_id

        endpoint = self.DATA_QUERY_ENDPOINT.format(
            username,
            api_key,
            trans_id
        ).replace('  ', '')

        return endpoint

    def format_airtime_endpoint(self, **kwargs):
        username = self.API_USERNAME
        api_key = self.API_KEY
        network = kwargs['network']
        phone_number = kwargs['phone_number']
        price = kwargs['price']
        trans_id = kwargs['transaction_id']

        endpoint = self.AIRTIME_ENDPOINT.format(
            username,
            api_key,
            network,
            phone_number,
            price,
            trans_id
        ).replace('  ', '')

        return endpoint

    def format_airtime_query_endoint(self, transaction_id):
        username = self.API_USERNAME
        api_key = self.API_KEY
        trans_id = transaction_id

        endpoint = self.AIRTIME_QUERY_ENDPOINT.format(
            username,
            api_key,
            trans_id
        ).replace('  ', '')

        return endpoint

    def make_transaction_id(self):
        is_valid = False

        while not is_valid:
            if len(list(Order.objects.values_list('transaction_id', flat=True))) > 0:
                last_id = list(Order.objects.values_list('transaction_id', flat=True))[-1]
            else:
                last_id = 1000

            transaction_id = last_id + random.randint(0, 9)
            if transaction_id not in list(Order.objects.values_list('transaction_id', flat=True)):
                is_valid = True

        return transaction_id

    def get_data_pricing(self):
        networks = self.DATA_CONFIG
        nets = []

        for n in networks.keys():
            for k in networks[n].keys():
                net = networks[n][k]
                net['network'] = n
                nets.append(net)

        return nets

    def get_product(self, product_code):
        networks = self.DATA_CONFIG
        product = {}

        for i in networks.keys():
            product = {**product, **networks[i]}

        product = product[product_code]

        return product
