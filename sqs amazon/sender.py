import boto3
from time import sleep
from worker import get_env_variable

# Create SQS client
sqs = boto3.client('sqs')

SQS_URL = get_env_variable("SQS_URL")

# Send message to SQS queue

count = 0
while True:
    count+=1
    response = sqs.send_message(
        QueueUrl=SQS_URL,
        DelaySeconds=2,
        MessageAttributes={
            'Author': {
                'DataType': 'String',
                'StringValue': 'Bryi'
            }
        },
        MessageBody=(
            f'Its message number {int(count)}'
        )
    )
    print(response['MessageId'])
    sleep(2)