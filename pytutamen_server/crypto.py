# -*- coding: utf-8 -*-


# Andy Sayler
# Copyright 2015


### Imports ###

import datetime
import uuid

ONE_DAY = datetime.timedelta(1, 0, 0)
ONE_MONTH = datetime.timedelta(28, 0, 0)
ONE_YEAR = datetime.timedelta(365, 0, 0)

from cryptography import x509
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization


### Functions ###

def csr_to_crt(csr_pem, ca_crt_pem, ca_key_pem, password=None,
               common_name=None, duration=None, serial=None):

    if isinstance(csr_pem, str):
        csr_pem = csr_pem.encode()
    if isinstance(ca_key_pem, str):
        ca_key_pem = ca_key_pem.encode()
    if isinstance(ca_crt_pem, str):
        ca_crt_pem = ca_crt_pem.encode()

    be = backends.default_backend()
    csr = x509.load_pem_x509_csr(csr_pem, be)
    ca_crt = x509.load_pem_x509_certificate(ca_crt_pem, be)
    ca_key = serialization.load_pem_private_key(ca_key_pem, password, be)

    if not common_name:
        common_name = csr.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    if not duration:
        duration = ONE_YEAR
    if not serial:
        serial = int(uuid.uuid4())

    sub_attr = []
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.COUNTRY_NAME)
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.LOCALITY_NAME)
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.STATE_OR_PROVINCE_NAME)
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)
    sub_attr += csr.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATIONAL_UNIT_NAME)
    sub_attr.append(x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name))

    builder = x509.CertificateBuilder()
    builder = builder.issuer_name(ca_crt.subject)
    builder = builder.subject_name(x509.Name(sub_attr))
    builder = builder.not_valid_before(datetime.datetime.today() - ONE_DAY)
    builder = builder.not_valid_after(datetime.datetime.today() + duration)
    builder = builder.serial_number(serial)
    builder = builder.public_key(csr.public_key())

    extensions = []
    extensions.append(x509.BasicConstraints(ca=False, path_length=None))
    for ext in extensions:
        builder = builder.add_extension(ext, critical=True)

    crt = builder.sign(private_key=ca_key, algorithm=hashes.SHA256(), backend=be)
    crt_pem = crt.public_bytes(serialization.Encoding.PEM)

    return crt_pem.decode()
