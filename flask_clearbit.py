#
# Flask-Clearbit
#
# Copyright (C) 2017 Boris Raicheff
# All rights reserved
#


import hashlib
import hmac
import logging

import clearbit
import itsdangerous

from flask import Response, abort, request, url_for
from flask.signals import Namespace
from six.moves.http_client import BAD_REQUEST, OK


logger = logging.getLogger('Flask-Clearbit')


clearbit_result = Namespace().signal('clearbit.result')


class Clearbit(object):
    """
    Flask-Clearbit

    Documentation:
    https://flask-clearbit.readthedocs.io

    API:
    https://clearbit.com/docs?python

    :param app: Flask app to initialize with. Defaults to `None`
    :param blueprint: Blueprint to attach the webhook handler to. Defaults to `None`
    """

    api_key = None

    blueprint = None

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
            self.blueprint = blueprint

    def handle_webhook(self):
        """
        https://clearbit.com/docs?python#webhooks
        """

        request_signature = request.headers.get('x-request-signature')
        if request_signature is None:
            abort(BAD_REQUEST)

        algorithm, signature = request_signature.split('=')
        if not all((algorithm == 'sha1', signature)):
            abort(BAD_REQUEST)

        digest = hmac.new(self.api_key.encode(), request.data, hashlib.sha1).hexdigest()
        if not itsdangerous.constant_time_compare(digest, signature):
            abort(BAD_REQUEST)

        clearbit_result.send(self, result=request.get_json())

        return Response(status=OK)

    @property
    def webhook_url(self):
        if self.blueprint is not None:
            return url_for('.'.join((self.blueprint.name, 'clearbit')), _external=True)

    def __getattr__(self, name):
        return getattr(clearbit, name)


# EOF
