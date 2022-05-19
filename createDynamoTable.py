import boto3
from botocore.config import Config
import os

config = Config(
    connect_timeout=3, read_timeout=3,
    retries={'max_attempts': 3})
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8007', config=config)
def dynamoTransformsTable():
    table = dynamodb.create_table(
        TableName="Transforms",
        KeySchema=[
            {
                'AttributeName': 'UUID',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'UUID',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    print(table)
dynamoTransformsTable()
