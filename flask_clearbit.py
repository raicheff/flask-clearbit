#
# Flask-Clearbit
#
# Copyright (C) 2016 Boris Raicheff
# All rights reserved
#


import hashlib
import hmac
import logging

import clearbit
import itsdangerous

from flask import Response, abort, request
from flask.signals import Namespace
from six.moves.http_client import BAD_REQUEST, OK


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

    api_key = None

    def __init__(self, app=None, blueprint=None):
        if app is not None:
            self.init_app(app, blueprint)

    def init_app(self, app, blueprint=None):
        self.api_key = api_key = app.config.get('CLEARBIT_KEY')
        if api_key is None:
            logger.warning('CLEARBIT_KEY not set')
            return
        clearbit.key = api_key
        if blueprint is not None:
            blueprint.add_url_rule('/clearbit', 'clearbit', self.handle_webhook, methods=['POST'])

    def handle_webhook(self):
        """
        https://clearbit.com/docs?python#webhooks
        """

        request_signature = request.headers.get('x-request-signature')
        if not request_signature:
            abort(BAD_REQUEST)

        algorithm, signature = request_signature.split('=')
        if not all((algorithm == 'sha1', signature)):
            abort(BAD_REQUEST)

        digest = hmac.new(self.api_key.encode(), request.data, hashlib.sha1).hexdigest()
        if not itsdangerous.constant_time_compare(digest, signature):
            abort(BAD_REQUEST)

        clearbit_result.send(self, payload=request.get_json())

        return Response(status=OK)

    def __getattr__(self, name):
        return getattr(clearbit, name)


# EOF
