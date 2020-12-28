#!/usr/bin/env python
import pika, sys, os
from time import sleep
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

load_dotenv()

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")
RABBIT_MQ = get_env_variable("RABBIT_MQ")

def main(POSTGRES_URL, POSTGRES_USER, POSTGRES_PW, POSTGRES_DB, RABBIT_MQ):

    #POSTGRESQL

    db_string = f'postgresql://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/{POSTGRES_DB}'

    db = create_engine(db_string)

    if not database_exists(db.url):
        create_database(db.url)
        print (f'DB {POSTGRES_DB} SUCCESSFULLY CREATED!')

    base = declarative_base()

    class Result(base):  
        __tablename__ = 'Results'

        id = Column(Integer, primary_key=True)
        result = Column(String)

    Session = sessionmaker(db)  
    session = Session()

    base.metadata.create_all(db)

    global count_msg
    count_msg = 0
    global result
    result = Result(id=int(count_msg), result='Success!')
    def add_to_db(count_msg, session):
        session.add(result)  
        session.commit()
        print(f'RESULT {count_msg} SUCCESSFULLY WRITED TO DB!')

    #RABBITMQ

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=str(RABBIT_MQ)))
    channel = connection.channel()

    channel.queue_declare(queue='hello', durable=True)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        sleep(body.count(b'.'))
        ch.basic_ack(delivery_tag = method.delivery_tag)
        global count_msg
        count_msg += 1
        add_to_db(count_msg, session)
        
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='hello', on_message_callback=callback)
    #add_to_db(count_msg, session)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main(POSTGRES_URL, POSTGRES_USER, POSTGRES_PW, POSTGRES_DB, RABBIT_MQ)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)