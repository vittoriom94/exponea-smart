import logging

MAX_FIRST_TIMEOUT_MS = 300
TIMEOUT_TOLERANCE = 0.2

EXPONEA_ENDPOINT = "https://exponea-engineering-assignment.appspot.com/api/work"

RETRIES = 2


def configure_logger():
    logging.basicConfig(level=logging.INFO, format="%(levelname)-9s %(asctime)s - %(name)s - %(message)s")
