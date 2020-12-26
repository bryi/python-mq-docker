#!/usr/bin/env python
import pika
from time import sleep

message = "Hello World!"
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
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

    sleep(3)

connection.close()