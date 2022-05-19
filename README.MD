## Pre-requisite
- Docker
- Docker-compose
- python

## Installation

Install boto3

```bash
pip install boto3
```

Run Docker Container

```bash
docker-compose up -d
```

Run python script

```bash
python3 createDynamoTable.py  
```

Check DynamoDB

```bash
aws dynamodb list-tables --endpoint-url http://localhost:8007
```