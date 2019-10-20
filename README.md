# Mailchimp Importer

## Credits

Based on work by [Tom Vass](mr.tom.vass@gmail.com).
The original repo available [here](https://github.com/Tomvass/Ometria).

## Description

Fetch contacts from Mailchimp API and send them to Ometria API.
After the first run, the importer only fetches records which have changed since its last run. This limits fetching
and pushing data unnecessarily.

Twisted is used as the task loop and Prometheus is used for error reporting.


## Improvements to Tom's work

* Filtering fields from Mailchimp to limit data fetch size
* Matching Mailchimp `unique_email_id` to Ometria ID
* Docker-compose
* More tests!
* Error handling
* Only update last updated time on successful response from Ometria
* Code layout
* Logging


## Getting started

* Create a .env file with the following environment variables

```
MAILCHIMP_API_KEY=<your key>
OMETRIA_API_KEY=<your key>
MAILCHIMP_LIST_ID=<list id>
```

* Build the Docker image using `docker-compose build`


## Running Ingest

* `docker-compose up`
* Browse to localhost:8888 to see Prometheus error reports


## Running Tests

* `docker-compose run ingest python -m ingest.tests`

