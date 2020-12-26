#!/usr/bin/env python
import pika
import sys
from time import sleep

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = "info: Hello World!"
while True:
    channel.basic_publish(exchange='logs', routing_key='', body=message)
    print(" [x] Sent %r" % message)
    sleep(3)

connection.close()