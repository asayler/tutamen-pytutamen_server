# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as dso
from pcollections import factories as dsf
from pcollections import keys as dsk


### Exceptions ###

class ObjectDNE(Exception):

    def __init__(self, key):

        # Call Parent
        msg = "Object '{:s}' does not exist".format(key)
        super().__init__(msg)



### Objects ###

class TransactionServer(object):

    prefix = "transactionsrv"
    type_transaction = dso.MutableSet
    key_transactions = "transactions"
    type_pending = dso.MutableList
    key_pending = "pending"

    def __init__(self, ds_driver):

        # Call Parent
        super().__init__()

        # Save Attrs
        self._driver = ds_driver

        # Setup Driver-Bound Factories

        self._srv_f_transactions = dsf.InstanceFactory(self._driver, self.type_transactions,
                                                       key_type=dsk.StrKey)
        self._srv_f_pending = dsf.InstanceFactory(self._driver, self.type_pending,
                                                  key_type=dsk.StrKey)
        self._trs_f_state = dsf.InstanceFactory(self._driver, Transaction.type_state,
                                                key_type=dsk.UUIDKey,
                                                key_kwargs={'prefix': Transaction.prefix,
                                                            'postfix': Transaction.postfix_state})
        self._trs_f_metadata = dsf.InstanceFactory(self._driver, Transaction.type_metadata,
                                                   key_type=dsk.UUIDKey,
                                                   key_kwargs={'prefix': Transaction.prefix,
                                                               'postfix': Transaction.postfix_metadata})
        self._trs_f_args = dsf.InstanceFactory(self._driver, Transaction.type_args,
                                               key_type=dsk.UUIDKey,
                                               key_kwargs={'prefix': Transaction.prefix,
                                                           'postfix': Transaction.postfix_args})
        self._trs_f_kwargs = dsf.InstanceFactory(self._driver, Transaction.type_kwargs,
                                                 key_type=dsk.UUIDKey,
                                                 key_kwargs={'prefix': Transaction.prefix,
                                                             'postfix': Transaction.postfix_kwargs})


        # Setup Local Collections

        k = "{:s}_{:s}".format(self.prefix, self.key_transactions)
        self._transactions = self._srv_f_transactions.from_raw(k)
        if not self._transactions.exists():
            self._transactions.create(set())

        k = "{:s}_{:s}".format(self.prefix, self.key_pending)
        self._pending = self._srv_f_transactions.from_raw(k)
        if not self._pending.exists():
            self._pending.create(list())

    def wipe(self):
        self._transactions.rem()
        self._pending.rem()

    def transaction_register(self, transaction):
        self._transactions.add(transaction.uid)
        transaction._state.set_val("pending")
        self._pending.append(transaction.uid)

    def transaction_unregister(self, transaction):
        if transaction.uid in self._pending:
            self._pending.remove(transaction.uid)
        self._transactions.discard(transaction.uid)

    def transaction_exists(self, transaction):
        return transaction.uid in self._transactions

    def transaction_from_new(self, metadata, *args, **kwargs):
        """New Transaction Constructor"""

        uid = uuid.uuid4()
        st = self._trs_f_status.from_new(uid, "init")
        md = self._trs_f_metadata.from_new(uid, metadata)
        ar = self._trs_f_args.from_new(uid, args)
        kw = self._trs_f_kwargs.from_new(uid, kwargs)
        trs = Transaction(self, uid, st, md, ar, kw)
        self.transaction_register(trs)
        return trs

    def transaction_from_existing(self, uid):
        """Existing Transaction Constructor"""

        # Check input
        if not uid in self._transactions:
            raise ObjectDNE(uid)

        uid = uuid.UUID(uid)
        st = self._trs_f_status.from_existing(uid)
        md = self._trs_f_metadata.from_existing(uid)
        ar = self._trs_f_args.from_existing(uid)
        kw = self._trs_f_kwargs.from_existing(uid)
        trs = Transaction(self, uid, st, md, ar, kw)
        return trs

class Transaction(object):

    prefix = "transaction"
    type_uid = uuid.UUID
    type_state = dso.MutableString
    postfix_state = "state"
    type_metadata = dso.Dictionary
    postfix_metadata = "metadata"
    type_args = dso.List
    postfix_args = "args"
    type_kwargs = dso.Dictionary
    postfix_kwargs = "kwargs"

    def __init__(self, srv, uid, state, metadata, args, kwargs):
        """Initialize Transaction"""

        # Call Parent
        super().__init__()

        # Check Args
        if not isinstance(srv, TransactionServer):
            msg = "'srv' must be of type '{}', ".format(TransactionServer)
            msg += "not '{}'".format(type(srv))
            raise TypeError(msg)
        if not isinstance(uid, self.type_uid):
            msg = "'uid' must be of type '{}', ".format(self.type_uid)
            msg += "not '{}'".format(type(uid))
            raise TypeError(msg)
        if not isinstance(state, self.type_state):
            msg = "'state' must be of type '{}', ".format(self.type_state)
            msg += "not '{}'".format(type(state))
            raise TypeError(msg)
        if not isinstance(metadata, self.type_metadata):
            msg = "'metadata' must be of type '{}', ".format(self.type_metadata)
            msg += "not '{}'".format(type(metadata))
            raise TypeError(msg)
        if not isinstance(args, self.type_args):
            msg = "'args' must be of type '{}', ".format(self.type_args)
            msg += "not '{}'".format(type(args))
            raise TypeError(msg)
        if not isinstance(kwargs, self.type_kwargs):
            msg = "'kwargs' must be of type '{}', ".format(self.type_kwargs)
            msg += "not '{}'".format(type(kwargs))
            raise TypeError(msg)

        # Save Attrs
        self._srv = srv
        self._uid = uid
        self._state = state
        self._metadata = metadata
        self._args = args
        self._kwargs = kwargs

    @property
    def uid(self):
        """Return Transaction UUID"""
        return str(self._uid)

    @property
    def state(self):
        """Return Transaction State"""
        return str(self._state)

    @property
    def metadata(self):
        """Return Transaction Metadata"""
        return str(self._metadata)

    @property
    def args(self):
        """Return Transaction args"""
        return str(self._args)

    @property
    def kwargs(self):
        """Return Transaction kwargs"""
        return str(self._kwargs)

    def exists(self):
        """Transaction Exists?"""
        return self._srv.transaction_exists(self)

    def rem(self):
        """Delete Transaction"""
        self._srv.transaction_unregister(self)
        self._state.rem()
        self._metadata.rem()
        self._args.rem()
        self._kwargs.rem()
