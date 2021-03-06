# -*- coding: utf-8 -*-


# Andy Sayler
# Copyright 2015


### Imports ###

import datetime
import uuid
import logging

import jwt

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from . import constants


### Constants ###

TYPE_RSA = 'RSA'

SIG_SHA256 = 'SHA256'

_RSA_SUPPORTED_LENGTH = [2048, 4096]
_RSA_SUPPORTED_EXP = [3, 65537]

JWT_RSA_SHA256 = 'RS256'
JWT_RSA_SHA384 = 'RS384'
JWT_RSA_SHA512 = 'RS512'

_JWT_SUPPORTED_ALGO = [JWT_RSA_SHA256, JWT_RSA_SHA384, JWT_RSA_SHA512]


### Logging ###

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())


### Functions ###

def gen_key(length=None, pub_exp=None, typ=None, raw=False, password=None):

    if not length:
        length = 4096
    if not pub_exp:
        pub_exp = 65537
    if not typ:
        typ = TYPE_RSA
    if isinstance(password, str):
        password = password.encode()

    if length not in _RSA_SUPPORTED_LENGTH:
        raise TypeError("Length must be one of '{}'".format(_RSA_SUPPORTED_LENGTH))
    if pub_exp not in _RSA_SUPPORTED_EXP:
        raise TypeError("pub_exp must be one of '{}'".format(_RSA_SUPPORTED_EXP))
    if typ != TYPE_RSA:
        raise TypeError("Only type '{}' supported".format(TYPE_RSA))

    priv_key = rsa.generate_private_key(pub_exp, length, default_backend())

    if raw:
        return priv_key
    else:
        if not password:
            encryption = serialization.NoEncryption()
        else:
            encryption = serialization.BestAvailableEncryption(password)
        priv_pem = priv_key.private_bytes(encoding=serialization.Encoding.PEM,
                                          format=serialization.PrivateFormat.PKCS8,
                                          encryption_algorithm=encryption)
        return priv_pem.decode()

def gen_key_pair(length=None, pub_exp=None, typ=None, raw=False, password=None,
                 priv_key_pem=None):

    if isinstance(password, str):
        password = password.encode()
    if isinstance(priv_key_pem, str):
        priv_key_pem = priv_key_pem.encode()

    if priv_key_pem:
        priv_key = serialization.load_pem_private_key(priv_key_pem, password,
                                                      default_backend())
    else:
        priv_key = gen_key(length=length, pub_exp=pub_exp, typ=typ, raw=True)

    pub_key = priv_key.public_key()

    if raw:
        return pub_key, priv_key
    else:
        if not password:
            encryption = serialization.NoEncryption()
        else:
            encryption = serialization.BestAvailableEncryption(password)
        priv_pem = priv_key.private_bytes(encoding=serialization.Encoding.PEM,
                                          format=serialization.PrivateFormat.PKCS8,
                                          encryption_algorithm=encryption)
        pub_pem = pub_key.public_bytes(encoding=serialization.Encoding.PEM,
                                       format=serialization.PublicFormat.SubjectPublicKeyInfo)
        return pub_pem.decode(), priv_pem.decode()

def gen_ca_pair(cn, country, state, locality, org, ou, email,
                duration=None, serial=None, ca_key_pem=None, password=None,
                length=None, pub_exp=None, typ=None, sig=SIG_SHA256):

    if not duration:
        duration = constants.DUR_TEN_YEAR
    if not serial:
        serial = uuid.uuid4()
    if sig != SIG_SHA256:
        raise TypeError("Only sig '{}' supported".format(SIG_SHA256))

    be = default_backend()

    if isinstance(ca_key_pem, str):
        ca_key_pem = ca_key_pem.encode()

    if isinstance(password, str):
        password = password.encode()

    if ca_key_pem:
        ca_key = serialization.load_pem_private_key(ca_key_pem, password, be)
    else:
        ca_key = gen_key(length=length, pub_exp=pub_exp, typ=typ, raw=True)

    sub_attr = []
    sub_attr.append(x509.NameAttribute(x509.NameOID.COMMON_NAME, cn))
    sub_attr.append(x509.NameAttribute(x509.NameOID.COUNTRY_NAME, country))
    sub_attr.append(x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, state))
    sub_attr.append(x509.NameAttribute(x509.NameOID.LOCALITY_NAME, locality))
    sub_attr.append(x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, org))
    sub_attr.append(x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME, ou))
    sub_attr.append(x509.NameAttribute(x509.NameOID.EMAIL_ADDRESS, email))

    builder = x509.CertificateBuilder()
    builder = builder.issuer_name(x509.Name(sub_attr))
    builder = builder.subject_name(x509.Name(sub_attr))
    builder = builder.not_valid_before(datetime.datetime.today() - constants.DUR_ONE_DAY)
    builder = builder.not_valid_after(datetime.datetime.today() + duration)
    builder = builder.serial_number(int(serial))
    builder = builder.public_key(ca_key.public_key())

    extensions = []
    extensions.append(x509.BasicConstraints(ca=True, path_length=1))
    for ext in extensions:
        builder = builder.add_extension(ext, critical=True)

    ca_crt = builder.sign(private_key=ca_key, algorithm=hashes.SHA256(), backend=be)
    ca_crt_pem = ca_crt.public_bytes(serialization.Encoding.PEM).decode()
    if not password:
        encryption = serialization.NoEncryption()
    else:
        encryption = serialization.BestAvailableEncryption(password)
    ca_key_pem = ca_key.private_bytes(encoding=serialization.Encoding.PEM,
                                      format=serialization.PrivateFormat.PKCS8,
                                      encryption_algorithm=encryption).decode()

    return (ca_crt_pem, ca_key_pem)

def csr_to_crt(csr_pem, ca_crt_pem, ca_key_pem, password=None,
               cn=None, ou=None, org=None, serial=None,
               duration=None):

    logger.debug("csr_pem:\n{}".format(csr_pem))
    logger.debug("cn: {}".format(cn))
    logger.debug("ou: {}".format(ou))
    logger.debug("org: {}".format(org))
    logger.debug("duration: {}".format(duration))
    logger.debug("serial: {}".format(serial))

    if isinstance(csr_pem, str):
        csr_pem = csr_pem.encode()
    if isinstance(ca_key_pem, str):
        ca_key_pem = ca_key_pem.encode()
    if isinstance(ca_crt_pem, str):
        ca_crt_pem = ca_crt_pem.encode()
    if isinstance(password, str):
        password = password.encode()

    be = default_backend()
    csr = x509.load_pem_x509_csr(csr_pem, be)
    ca_crt = x509.load_pem_x509_certificate(ca_crt_pem, be)
    ca_key = serialization.load_pem_private_key(ca_key_pem, password, be)

    if not cn:
        cn = csr.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    if not ou:
        ou = csr.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
    if not org:
        org = csr.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value
    if not duration:
        duration = constants.DUR_ONE_YEAR
    if not serial:
        serial = uuid.uuid4()

    sub_attrs = []
    sub_attrs += csr.subject.get_attributes_for_oid(x509.NameOID.COUNTRY_NAME)
    sub_attrs += csr.subject.get_attributes_for_oid(x509.NameOID.LOCALITY_NAME)
    sub_attrs += csr.subject.get_attributes_for_oid(x509.NameOID.STATE_OR_PROVINCE_NAME)
    sub_attrs.append(x509.NameAttribute(x509.NameOID.COMMON_NAME, cn))
    sub_attrs.append(x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME, ou))
    sub_attrs.append(x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, org))

    logger.debug("sub_attr: {}".format(sub_attrs))

    builder = x509.CertificateBuilder()
    builder = builder.issuer_name(ca_crt.subject)
    builder = builder.subject_name(x509.Name(sub_attrs))
    builder = builder.not_valid_before(datetime.datetime.today() - constants.DUR_ONE_DAY)
    builder = builder.not_valid_after(datetime.datetime.today() + duration)
    builder = builder.serial_number(int(serial))
    builder = builder.public_key(csr.public_key())

    extensions = []
    extensions.append(x509.BasicConstraints(ca=False, path_length=None))

    logger.debug("extensions: {}".format(extensions))

    for ext in extensions:
        builder = builder.add_extension(ext, critical=True)

    crt = builder.sign(private_key=ca_key, algorithm=hashes.SHA256(), backend=be)
    crt_pem = crt.public_bytes(serialization.Encoding.PEM).decode()

    logger.debug("crt_pem:\n{}".format(crt_pem))

    return crt_pem

def sign_jwt(val, priv_key, algorithm=JWT_RSA_SHA256):

    if not algorithm in _JWT_SUPPORTED_ALGO:
        raise TypeError("algorithm must be one of '{}'".format(_JWT_SUPPORTED_ALGO))

    out = jwt.encode(val, priv_key, algorithm=algorithm)
    return out.decode()

def verify_jwt(val, pub_key, algorithm=JWT_RSA_SHA256):

    if not algorithm in _JWT_SUPPORTED_ALGO:
        raise TypeError("algorithm must be one of '{}'".format(_JWT_SUPPORTED_ALGO))

    if isinstance(val, str):
        val = val.encode()
    return jwt.decode(val, pub_key, algorithm=algorithm)
