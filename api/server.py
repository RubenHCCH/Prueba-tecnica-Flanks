import pymongo
from quart import Quart, jsonify, request
from mongo_collection import get_db_collection
from datetime import datetime

app = Quart(__name__)
collection = get_db_collection()


def format_date(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')


def format_timestamp(date_string):
    return datetime.fromisoformat(date_string).timestamp()


def extract_transaction_info(t):
    address_from = t['baseTransactions'][0]['addressHash']
    address_to = t['baseTransactions'][3]['addressHash']
    transaction_fee = t['baseTransactions'][1]['amount'] + t['baseTransactions'][2]['amount']
    created_time = format_date(t["createTime"])
    attachment_time = format_date(t["attachmentTime"])

    return {'createTime': created_time,
            'transactionHash': t["_id"],
            'addressFrom': address_from,
            'addressTo': address_to,
            'transactionType': t["type"],
            'amount': t["amount"],
            'transactionFee': transaction_fee,
            'confirmationDate': attachment_time}


def get_results(documents):
    return [extract_transaction_info(d) for d in documents]


async def filter_by_date():
    date_after = request.args.get('dateAfter', type=format_timestamp)
    date_before = request.args.get('dateBefore', type=format_timestamp)
    return await verify_dates(date_after, date_before)


async def verify_dates(date_after, date_before):
    if date_after is None:
        date_after = 0
    if date_before is None:
        date_before = 253370764800
    return date_after, date_before


@app.route("/transactions")
async def index():
    date_after, date_before = await filter_by_date()
    documents = collection.find({"createTime": {
                                    "$gte": date_after,
                                    "$lte": date_before}
                                 }).sort("createTime", pymongo.DESCENDING)
    result = get_results(documents)
    return jsonify({'transactions': result})


@app.route("/transactions/<address_from>/received")
async def received_from(address_from):
    date_after, date_before = await filter_by_date()
    documents = collection.find({"baseTransactions.0.addressHash": address_from,
                                 "createTime": {
                                     "$gte": date_after,
                                     "$lte": date_before}
                                 }).sort("createTime", pymongo.DESCENDING)
    result = get_results(documents)
    return jsonify({'transactions': result})


@app.route("/transactions/<address_to>/sent")
async def sent_to(address_to):
    date_after, date_before = await filter_by_date()
    documents = collection.find({"baseTransactions.3.addressHash": address_to,
                                 "createTime": {
                                     "$gte": date_after,
                                     "$lte": date_before}
                                 }).sort("createTime", pymongo.DESCENDING)
    result = get_results(documents)
    return jsonify({'transactions': result})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
