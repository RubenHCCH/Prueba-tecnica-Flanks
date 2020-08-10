import gspread
import logging
import sys
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

from rabbitMQ_channel import get_queue_channel, queue_name
from mongo_collection import get_db_collection


def get_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(credentials)
    return client.open(gsheet_name).sheet1


def insert_top_row(doc_info):
    sheet.insert_row(doc_info, 1)


def format_date(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')


def extract_doc_info(doc):
    address_from = doc['baseTransactions'][0]['addressHash']
    address_to = doc['baseTransactions'][3]['addressHash']
    transaction_fee = doc['baseTransactions'][1]['amount'] + doc['baseTransactions'][2]['amount']
    created_time = format_date(doc["createTime"])
    attachment_time = format_date(doc["attachmentTime"])

    return [created_time, doc["_id"], address_from, address_to, doc["type"], doc["amount"],
            transaction_fee, attachment_time]


def update_spread_sheet(transaction_hash):
    doc = collection.find_one(transaction_hash)
    doc_info = extract_doc_info(doc)
    insert_top_row(doc_info)


def callback(ch, method, properties, body):
    try:
        update_spread_sheet(body.decode())
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(e)


def main():
    channel = get_queue_channel()
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

gsheet_name = os.getenv("GSHEET_NAME")
collection = get_db_collection()
sheet = get_gsheet()

if __name__ == '__main__':
    main()

