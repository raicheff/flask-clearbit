#
# Flask-FileRev
#
# Copyright (C) 2016 Boris Raicheff
# All rights reserved
#


import hashlib
import hmac
import logging

try:
    # Python 2
    from httplib import BAD_REQUEST, OK
except ImportError:
    # Python 3+
    from http.client import BAD_REQUEST, OK

import clearbit
import itsdangerous

from flask import Response, abort, current_app, request
from flask.signals import Namespace


__all__ = ('Clearbit', 'clearbit_result')

__version__ = '0.1.1'


logger = logging.getLogger('Flask-Clearbit')

namespace = Namespace()

clearbit_result = namespace.signal('clearbit.result')


class Clearbit(object):
    """
    Flask-Clearbit

    Refer to http://flask-clearbit.readthedocs.org for
    more details.

    :param app: Flask app to initialize with. Defaults to `None`
    """

    def __init__(self, app=None, blueprint=None):
        if app is not None:
            self.init_app(app, blueprint)

    def init_app(self, app, blueprint=None):
        clearbit_key = app.config.get('CLEARBIT_KEY')
        if clearbit_key is None:
            logger.warning('CLEARBIT_KEY not set')
            return
        clearbit.key = clearbit_key
        if blueprint is not None:
            blueprint.add_url_rule('/clearbit', 'clearbit', webhooks, methods=['POST'])


def webhooks():
    """
    https://clearbit.com/docs?python#webhooks
    """

    request_signature = request.headers.get('x-request-signature')
    if not request_signature:
        abort(BAD_REQUEST)

    algorithm, signature = request_signature.split('=')
    if not all((algorithm == 'sha1', signature)):
        abort(BAD_REQUEST)

    key = current_app.config.get('CLEARBIT_KEY')
    message = request.data
    digest = hmac.new(key, message, hashlib.sha1).hexdigest()
    if not itsdangerous.constant_time_compare(digest, str(signature)):
        abort(BAD_REQUEST)

    payload = request.get_json()
    webhook_id = payload.get('id')
    logger.info('webhook_id=%s', webhook_id)
    clearbit_result.send(current_app._get_current_object(), payload=payload)

    return Response(status=OK)


# EOF
