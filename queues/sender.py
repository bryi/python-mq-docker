#!/usr/bin/env python
import pika
from time import sleep
from worker import get_env_variable

message = "Hello World!"
RABBIT_MQ = get_env_variable("RABBIT_MQ")
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_MQ))
channel = connection.channel()
channel.queue_declare(queue='hello', durable=True)

while True:
    channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
    
    print(f"[x] Sent {message}")

    sleep(1)

connection.close()