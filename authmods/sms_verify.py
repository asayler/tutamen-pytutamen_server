# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2016


### Imports ###

import logging
import os
import time
import datetime

from twilio.rest import TwilioRestClient

from pytutamen_server import constants


### Constants ###

_TIMEOUT = constants.DUR_ONE_MINUTE
_SLEEP = 3

### Logging ###

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())


### Authmod ###

class Authmod(object):

    def __init__(self, authenticator, account_sid=None, auth_token=None, sender=None):

        # Call Parent
        super().__init__()

        # Process Args
        if not account_sid:
            account_sid = authenticator.userdata.get('account_sid', None)
            if not account_sid:
                raise TypeError("account_sid required")
        if not auth_token:
            auth_token = authenticator.userdata.get('auth_token', None)
            if not auth_token:
                raise TypeError("auth_token required")
        if not sender:
            sender = authenticator.userdata.get('sender', None)
            if not sender:
                raise TypeError("sender required")

        # Save Args
        self._authenticator = authenticator
        self._twilio = TwilioRestClient(account_sid, auth_token)
        self._sender = sender

    def run(self, authorization):

        nonce = int.from_bytes(os.urandom(2), 'little')

        sender = self._sender
        # Todo: extract this from Account userdata
        recipient = self._authenticator.userdata.get('recipient')

        # Setup message
        body = "Account {}: ".format(str(authorization.accountuid))
        body += "{} ".format(authorization.objtype)
        if authorization.objuid:
            body += "{} ".format(str(authorization.objuid))
        body += "{} - ".format(authorization.objperm)
        body += "Reply '{}' to approve.".format(str(nonce))

        # Send message
        logger.debug("Sending message '{}' from {} to {}".format(body, sender, recipient))
        message = self._twilio.messages.create(to=recipient, from_=sender, body=body)

        # Poll for response
        start_utc = datetime.datetime.utcnow()
        deadline_utc = start_utc + _TIMEOUT
        while datetime.datetime.utcnow() < deadline_utc:
            yesterday_utc = datetime.datetime.utcnow().date() - constants.DUR_ONE_DAY
            lst = self._twilio.messages.list(to=sender, from_=recipient, after=yesterday_utc)
            logger.debug("Received messages '{}'".format(lst))
            for message in lst:
                logger.debug("message.date_sent: {}".format(message.date_sent))
                if message.date_sent > start_utc:
                    # Todo: Only count most recent message
                    logger.debug("message.body: {}".format(message.body))
                    if str(nonce) in message.body:
                        logger.debug("Nonce Found - Pass")
                        return True
            time.sleep(_SLEEP)

        logger.debug("No Nonce Found - Fail")
        return False
