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
docker-compose up -d --force-recreate &&  sudo chmod 777 ./docker/dynamodb
```

Run python script

```bash
python3 createDynamoTable.py  
```

Check DynamoDB

```bash
aws dynamodb list-tables --endpoint-url http://localhost:8007
```

## Local Database

Install Synth to generate database
```bash
cd postgres && cd synth_app && curl --proto '=https' --tlsv1.2 -sSL https://getsynth.com/install | sh
```

Run Docker Container
```bash
cd .. && docker-compose up -d
```

Get into Container to create source DB
```bash
docker exec -t <container_id> bash
su postgres
psql
\c postgres
```

Create Table and Schemas
```bash
CREATE DATABASE postgres;

CREATE TABLE companies(
   company_id SERIAL PRIMARY KEY,
   company_name VARCHAR(255) NOT NULL
);

CREATE TABLE contacts(
   contact_id SERIAL PRIMARY KEY,
   company_id INT,
   contact_name VARCHAR(255) NOT NULL,
   phone VARCHAR(25),
   email VARCHAR(100),
   CONSTRAINT fk_company
      FOREIGN KEY(company_id) 
      REFERENCES companies(company_id)
);
```

Generate Database
```bash
cd ./postgres/synth_app && synth generate gen/ --to postgres://postgres:postgres@localhost:5432
```