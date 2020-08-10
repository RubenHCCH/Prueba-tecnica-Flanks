import os
import sys
import requests
import logging
from pymongo.errors import DuplicateKeyError

from rabbitMQ_channel import get_queue_channel, queue_name
from mongo_collection import get_db_collection


def get_transactions_by_address(address):
    url = 'https://mainnet-fullnode1.coti.io/transaction/addressTransactions'
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    body_data = '{"address": "%s"}' % address
    response = requests.post(url, headers=headers, data=body_data)
    return response.json()['transactionsData']


def get_data_by_address(address):
    try:
        return get_transactions_by_address(address)
    except Exception as e:
        logging.critical(e)
        sys.exit("Could not get data")


def add_to_queue(transaction_id):
    channel.basic_publish(exchange='', routing_key=queue_name, body=transaction_id)


def save_transaction(transaction):
    transaction_id = transaction.pop("hash")
    transaction["_id"] = transaction_id
    try:
        collection.insert_one(transaction)
        add_to_queue(transaction_id)
    except DuplicateKeyError:
        pass
    except Exception as e:
        logging.error(e)


def main():
    logging.info(f"Starting to collect data, Address: {client_address}")
    data = get_data_by_address(client_address)
    for trans in data:
        save_transaction(trans)
    logging.info(f"Task finished successfully")


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
client_address = os.getenv("CLIENT_ADDRESS")
channel = get_queue_channel()
collection = get_db_collection()

if __name__ == '__main__':
    main()

