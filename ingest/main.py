import logging

from prometheus_client import start_http_server
from twisted.internet import reactor, task
from twisted.python import log

from .config import MAILCHIMP_API_KEY, OMETRIA_API_KEY, DEFAULT_SYNC_TIME
from .ingester import MailchimpAPIImporter

# Log to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)

# add the handler to the root logger
# logging.getLogger('').addHandler(console)
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    # Start Prometheus metrics for reporting
    start_http_server(8888)

    # Create new controller and run sync every N seconds
    i = MailchimpAPIImporter(MAILCHIMP_API_KEY, OMETRIA_API_KEY)
    # Loop forever
    # Could start multiple of these hand have twisted run them at arbitrary times
    loop = task.LoopingCall(i.run)
    loop.start(DEFAULT_SYNC_TIME).addErrback(log.err)
    reactor.run()
