#!/usr/bin/env python
import pika
from time import sleep

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='hello')

while True:
    channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')
    
    print(" [x] Sent 'Hello World!'")

    sleep(3)

connection.close()