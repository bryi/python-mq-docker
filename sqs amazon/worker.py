#!/usr/bin/env python
import sys, boto3, os
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
SQS_URL = get_env_variable("SQS_URL")

def main(POSTGRES_URL, POSTGRES_USER, POSTGRES_PW, POSTGRES_DB, SQS_URL):

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

    count_msgs = session.query(Result)
    counts = []
    for count in count_msgs:
        counts.append(count.id)
    try:
        count_msg = max(counts)
    except:
        count_msg = 0
    #global count
    count = count_msg
    #print(f'START COUNT {count}')
    global result
    
    def add_to_db(count, session):
        #print(count)
        result = Result(id=int(count), result='Success!')
        session.add(result)  
        session.commit()
        print(f'DB: RESULT {count} SUCCESSFULLY WRITED TO DB!')

    #SQS

    sqs = boto3.client('sqs')
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=SQS_URL,
                AttributeNames=[
                    'SentTimestamp'
                ],
                MaxNumberOfMessages=1,
                MessageAttributeNames=[
                    'All'
                ],
                VisibilityTimeout=0,
                WaitTimeSeconds=0
            )

            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            sqs.delete_message(
                QueueUrl=SQS_URL,
                ReceiptHandle=receipt_handle
            )
            count += 1
            add_to_db(count, session)
            print(f'WORKER: Number of received and deleted message: {count}')
        except:
            pass

if __name__ == '__main__':
    try:
        main(POSTGRES_URL, POSTGRES_USER, POSTGRES_PW, POSTGRES_DB, SQS_URL)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)