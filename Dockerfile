FROM python:3.7

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements.txt /requirements.txt

# Upgrade to the latest pip
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

WORKDIR /app
