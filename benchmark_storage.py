#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2016
# pytutamen_server tests


### Imports ###

## Future ##
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.utils import native_str
from builtins import *

## stdlib ##
import time

## extlib ##
from pcollections import drivers
from pcollections import backends

## pytutamen_server ##
from pytutamen_server import constants
from pytutamen_server import utility
from pytutamen_server import datatypes
from pytutamen_server import storage


_REDIS_DB = 9
_ITR = 1000
_TEST_SEC = "Test Secret 33"

if __name__ == '__main__':

    # Setup Connection
    pdriver = drivers.RedisDriver(db=_REDIS_DB)
    pbackend = backends.RedisAtomicBackend(pdriver)

    # Confirm Empty DB
    if (pdriver.redis.dbsize() != 0):
        raise Exception("DB Not Empty")


    itr = _ITR

    # Setup Secret
    srv = storage.StorageServer(pbackend, create=True)
    col = srv.collections.create(ac_servers=["https://acsrv.test"], ac_required=1)
    sec = col.secrets.create(data=_TEST_SEC)
    col_uid = col.uid
    sec_uid = sec.uid

    # Benchmark Srv Create
    print("Testing Server Create...")
    srv = None
    start = time.perf_counter()
    for i in range(itr):
        srv = storage.StorageServer(pbackend, create=False)
    end = time.perf_counter()
    dur = end - start
    iops = itr/dur
    print("iops ({} iterations) = {}".format(itr, iops))

    # Benchmark Col Get
    print("Testing Collection Get...")
    col = None
    start = time.perf_counter()
    for i in range(itr):
        col = srv.collections.get(uid=col_uid)
    end = time.perf_counter()
    assert(col.uid == col_uid)
    dur = end - start
    iops = itr/dur
    print("iops ({} iterations) = {}".format(itr, iops))

    # Benchmark Sec Get
    print("Testing Secret Get...")
    sec = None
    start = time.perf_counter()
    for i in range(itr):
        sec = col.secrets.get(uid=sec_uid)
    end = time.perf_counter()
    assert(sec.uid == sec_uid)
    dur = end - start
    iops = itr/dur
    print("iops ({} iterations) = {}".format(itr, iops))

    # Benchmark Data Get
    print("Testing Secret Data Get...")
    data = None
    start = time.perf_counter()
    for i in range(itr):
        data = sec.data
    end = time.perf_counter()
    assert(data == _TEST_SEC)
    dur = end - start
    iops = itr/dur
    print("iops ({} iterations) = {}".format(itr, iops))

    # Benchmark All
    print("Testing Full Stack Get...")
    srv = None
    col = None
    sec = None
    data = None
    start = time.perf_counter()
    for i in range(itr):
        srv = storage.StorageServer(pbackend, create=False)
        col = srv.collections.get(uid=col_uid)
        sec = col.secrets.get(uid=sec_uid)
        data = sec.data
    end = time.perf_counter()
    assert(data == _TEST_SEC)
    dur = end - start
    iops = itr/dur
    print("iops ({} iterations) = {}".format(itr, iops))

    # Clear DB
    pdriver.redis.flushdb()
