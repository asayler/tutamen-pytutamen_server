# -*- coding: utf-8 -*-


# Andy Sayler
# Copyright 2015


### Imports ###

import datetime
import uuid

DUR_ONE_DAY = datetime.timedelta(1, 0, 0)
DUR_ONE_MONTH = datetime.timedelta(28, 0, 0)
DUR_ONE_YEAR = datetime.timedelta(366, 0, 0)
DUR_TEN_YEAR = datetime.timedelta(3660, 0, 0)

TYPE_RSA = 'RSA'

SIG_SHA256 = 'SHA56'

_SUPPORTED_LENGTH = [2048, 4096]
_SUPPORTED_EXP = [3, 65537]

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

### Functions ###

def gen_ca_pair(cn, country, state, locality, organization, ou, email,
                duration=None, serial=None, ca_key_pem=None, password=None,
                length=4096, pub_exp=65537, typ=TYPE_RSA, sig=SIG_SHA256):

    if not duration:
        duration = DUR_TEN_YEAR
    if not serial:
        serial = uuid.uuid4()
    if length not in _SUPPORTED_LENGTH:
        raise TypeError("Length must be one of '{}'".format(_SUPPOERTED_LENGTH))
    if pub_exp not in _SUPPORTED_EXP:
        raise TypeError("pub_exp must be one of '{}'".format(_SUPPOERTED_EXP))
    if typ != TYPE_RSA:
        raise TypeError("Only type '{}' supported".format(TYPE_RSA))
    if sig != SIG_SHA256:
        raise TypeError("Only sig '{}' supported".format(SIG_SHA256))

    be = default_backend()

    if isinstance(ca_key_pem, str):
        ca_key_pem = ca_key_pem.encode()

    if isinstance(password, str):
        password = password.encode()

    if not ca_key_pem:
        ca_key = rsa.generate_private_key(pub_exp, length, be)
    else:
        ca_key = serialization.load_pem_private_key(ca_key_pem, password, be)

    sub_attr = []
    sub_attr.append(x509.NameAttribute(x509.NameOID.COMMON_NAME, cn))
    sub_attr.append(x509.NameAttribute(x509.NameOID.COUNTRY_NAME, country))
    sub_attr.append(x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, state))
    sub_attr.append(x509.NameAttribute(x509.NameOID.LOCALITY_NAME, locality))
    sub_attr.append(x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, organization))
    sub_attr.append(x509.NameAttribute(x509.NameOID.ORGANIZATIONAL_UNIT_NAME, ou))
    sub_attr.append(x509.NameAttribute(x509.NameOID.EMAIL_ADDRESS, email))

    builder = x509.CertificateBuilder()
    builder = builder.issuer_name(x509.Name(sub_attr))
    builder = builder.subject_name(x509.Name(sub_attr))
    builder = builder.not_valid_before(datetime.datetime.today() - DUR_ONE_DAY)
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
               cn=None, duration=None, serial=None):

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
    if not duration:
        duration = DUR_ONE_YEAR
    if not serial:
        serial = uuid.uuid4()

    sub_attr = []
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.COUNTRY_NAME)
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.LOCALITY_NAME)
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.STATE_OR_PROVINCE_NAME)
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATIONAL_UNIT_NAME)
    sub_attr.append(x509.NameAttribute(x509.NameOID.COMMON_NAME, cn))

    builder = x509.CertificateBuilder()
    builder = builder.issuer_name(ca_crt.subject)
    builder = builder.subject_name(x509.Name(sub_attr))
    builder = builder.not_valid_before(datetime.datetime.today() - DUR_ONE_DAY)
    builder = builder.not_valid_after(datetime.datetime.today() + duration)
    builder = builder.serial_number(int(serial))
    builder = builder.public_key(csr.public_key())

    extensions = []
    extensions.append(x509.BasicConstraints(ca=False, path_length=None))
    for ext in extensions:
        builder = builder.add_extension(ext, critical=True)

    crt = builder.sign(private_key=ca_key, algorithm=hashes.SHA256(), backend=be)
    crt_pem = crt.public_bytes(serialization.Encoding.PEM)

    return crt_pem.decode()
