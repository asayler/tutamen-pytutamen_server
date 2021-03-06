# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015, 2016


import datetime


DUR_ONE_MINUTE = datetime.timedelta(minutes=1)
DUR_ONE_HOUR = datetime.timedelta(hours=1)
DUR_ONE_DAY = datetime.timedelta(days=1)
DUR_ONE_MONTH = datetime.timedelta(days=28)
DUR_ONE_YEAR = datetime.timedelta(days=366)
DUR_TEN_YEAR = datetime.timedelta(days=3660)

KEY_OBJTYPE = "objtype"
KEY_OBJUID = "objuid"

TYPE_SRV_AC = "acserver"
TYPE_SRV_STORAGE = "storageserver"
SRV_TYPES = [TYPE_SRV_AC, TYPE_SRV_STORAGE]

TYPE_VERIFIER = "verifier"
TYPE_COL = "collection"
TYPE_AUTHENTICATOR = "authenticator"
UID_TYPES = [TYPE_COL, TYPE_VERIFIER, TYPE_AUTHENTICATOR]

PERM_CREATE = "create"
PERM_READ = "read"
PERM_MODIFY = "modify"
PERM_DELETE = "delete"
PERM_PERMS = "perms"
PERM_DEFAULT = "default"

AUTHZ_STATUS_NEW = "pending"
AUTHZ_STATUS_APPROVED = "approved"
AUTHZ_STATUS_DENIED = "denied"
AUTHZ_STATUS_FAILED = "failed"
