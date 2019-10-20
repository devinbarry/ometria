# Proof of concept for Mailchimp importer

Simple python task that queries mailchimp every hour for changes and pushes them to Ometria.


## Design

In it's most basic form this is a simple pull-push importer. We query the source for new information, do some basic translation (and verification) on the returned data before uploading it.


Due to time constraints I did not look into using webhooks. I don't know mailchimp very well so didn't feel comfortable spending the time required to discern what data I would recieve in a list webhook. However this would mean we could naturally be notified about changes in the list through a push system rather than a pull. I would need to weigh up the extra costs, whether mailchimp will be very chatty and send many updates in an hour or whether webhooks would keep Ometria up to data more accurately.


I have chosen to go with Prometheus for reporting. It's fully featured and super quick to get going. We can create easy to read dashboards, along with mail notifications on certrain thresholds by using something like Grafana.


I don't believe a Queue is neccessary here unless the transforms between mailchimp become expensive.

I did consider allowing multiple imports in the same script, however this added complexity for a simple PoC. If this was the desired approach I would include a basic CRUD API to update the list without having to restart the service. In this case I may elect to store configuration in a database however a simple text file would also be sufficient for a smaller number of importers.


## AWS considerations

This project could quite happily live inside a ec2 nano instance. But would be most suited to run inside a container. You could then create a new container for each importer.


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

