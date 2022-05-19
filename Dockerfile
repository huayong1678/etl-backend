# pull official base image
FROM python:3.9.0-slim-buster

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update \
  && apt-get -y install gcc postgresql \
  && apt-get clean

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# copy project
COPY . /code/

# collect static files
RUN python manage.py collectstatic --no-input