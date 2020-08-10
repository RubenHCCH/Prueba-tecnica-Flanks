import pika
import os

rabbit_host = os.getenv("RABBIT_HOST")
rabbit_user = os.getenv("RABBIT_USER")
rabbit_password = os.getenv("RABBIT_PASSWORD")
queue_name = os.getenv("QUEUE_NAME")


def get_queue_channel():
    credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    return channel
