import logging

from django.db import transaction

logger = logging.getLogger(__name__)


def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))

    return inner
