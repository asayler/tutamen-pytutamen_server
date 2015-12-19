#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Access Control Tests


### Imports ###

## stdlib ##
import functools
import time
import uuid
import unittest

# Tests Common
import tests_common

## tutamen_server ##
from pytutamen_server import accesscontrol

### Object Classes ###

class AccessControlTestCase(tests_common.BaseTestCase):

    def _create_accesscontrolserver(self):

        acs = accesscontrol.AccessControlServer(self.driver)
        return acs

    def _create_authorization(self, acs, direct=False, **kwargs_user):

        clientuid = uuid.uuid4()
        expiration = time.time()
        objperm = 'TESTPERM'
        objtype = 'TESTOBJ'
        objuid = uuid.uuid4()
        kwargs = {'clientuid': clientuid, 'expiration': expiration,
                  'objperm': objperm, 'objtype': objtype, 'objuid': objuid}
        kwargs.update(kwargs_user)

        if direct:
            authorization = accesscontrol.Authorization(acs, create=True, **kwargs)
        else:
            authorization = acs.authorizations_create(**kwargs)
        return authorization

    def _create_authenticator(self, acs, direct=False, **kwargs_user):

        module = 'TESTMOD'
        kwargs = {'module': module}
        kwargs.update(kwargs_user)

        if direct:
            authenticator = accesscontrol.Authenticator(acs, create=True, **kwargs)
        else:
            authenticator = acs.authenticators_create(**kwargs)
        return authenticator


        kwargs.update(kwargs_user)

        if direct:
        else:

class ObjectsHelpers(object):

    def helper_test_obj_create(self, srv, objtype, create_obj):

        # Create Object
        obj = create_obj(srv)
        self.assertIsInstance(obj, objtype)
        self.assertTrue(obj.exists())

        # Cleanup
        obj.destroy()

    def helper_test_obj_existing(self, srv, objtype, create_obj, get_obj):

        # Create Object
        obj = create_obj(srv)
        key = obj.key
        uid = obj.uid

        # Test get (key)
        obj = get_obj(key=key)
        self.assertIsInstance(obj, objtype)
        self.assertTrue(obj.exists())
        self.assertEqual(obj.key, key)
        self.assertEqual(obj.uid, uid)

        # Test get (uuid)
        obj = get_obj(uid=uid)
        self.assertIsInstance(obj, objtype)
        self.assertTrue(obj.exists())
        self.assertEqual(obj.key, key)
        self.assertEqual(obj.uid, uid)

        # Cleanup
        obj.destroy()

    def helper_test_objects_list(self, srv, objtype, create_objs, list_objs):

        # List Objects (Empty)
        keys = list_objs()
        self.assertEqual(len(keys), 0)

        # Create Objects
        objs = []
        for i in range(10):
            objs.append(create_objs(srv))

        # List Objects (Full)
        keys = list_objs()
        self.assertEqual(len(keys), len(objs))
        for obj in objs:
            self.assertTrue(obj.key in keys)

        # Delete Objects
        for obj in objs:
            obj.destroy()

        # List Objects (Empty)
        keys = list_objs()
        self.assertEqual(len(keys), 0)

    def helper_test_objects_exists(self, srv, objtype, create_objs, exists_objs):

        # Test DNE (key)
        key = "fakekey"
        self.assertFalse(exists_objs(key=key))

        # Test DNE (uuid)
        uid = uuid.uuid4()
        self.assertFalse(exists_objs(uid=uid))

        # Create Object
        obj = create_objs(srv)
        key = obj.key
        uid = obj.uid

        # Test Exists (key)
        self.assertTrue(exists_objs(key=key))

        # Test Exists (uuid)
        self.assertTrue(exists_objs(uid=uid))

        # Delete Object
        obj.destroy()

        # Test DNE (key)
        self.assertFalse(exists_objs(key=key))

        # Test DNE (uuid)
        self.assertFalse(exists_objs(uid=uid))

class AccessControlServerTestCase(AccessControlTestCase, ObjectsHelpers):

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

    # Core Tests #

    def test_init_and_destroy(self):

        # Create Server
        acs = self._create_accesscontrolserver()
        self.assertIsInstance(acs, accesscontrol.AccessControlServer)

        # Cleanup
        acs.destroy()

    # Authorization Tests #

    def test_authorizations_create(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Create
        create_obj = functools.partial(self._create_authorization, direct=False)
        self.helper_test_obj_create(acs, accesscontrol.Authorization,
                                    create_obj)

        # Cleanup
        acs.destroy()

    def test_authorizations_get(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Get
        create_obj = functools.partial(self._create_authorization, direct=False)
        get_obj = functools.partial(acs.authorizations_get)
        self.helper_test_obj_existing(acs, accesscontrol.Authorization,
                                      create_obj, get_obj)

        # Cleanup
        acs.destroy()

    def test_authorizations_list(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test List
        create_obj = functools.partial(self._create_authorization, direct=False)
        list_objs = functools.partial(acs.authorizations_list)
        self.helper_test_objects_list(acs, accesscontrol.Authorization,
                                      create_obj, list_objs)

        # Cleanup
        acs.destroy()

    def test_authorizations_exists(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Exists
        create_obj = functools.partial(self._create_authorization, direct=False)
        exists_obj = functools.partial(acs.authorizations_exists)
        self.helper_test_objects_exists(acs, accesscontrol.Authorization,
                                        create_obj, exists_obj)

        # Cleanup
        acs.destroy()

    # Authenticator Tests #

    def test_authenticators_create(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Create
        create_obj = functools.partial(self._create_authenticator, direct=False)
        self.helper_test_obj_create(acs, accesscontrol.Authenticator,
                                    create_obj)

        # Cleanup
        acs.destroy()

    def test_authenticators_get(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Get
        create_obj = functools.partial(self._create_authenticator, direct=False)
        get_obj = functools.partial(acs.authenticators_get)
        self.helper_test_obj_existing(acs, accesscontrol.Authenticator,
                                      create_obj, get_obj)

        # Cleanup
        acs.destroy()

    def test_authenticators_list(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test List
        create_obj = functools.partial(self._create_authenticator, direct=False)
        list_objs = functools.partial(acs.authenticators_list)
        self.helper_test_objects_list(acs, accesscontrol.Authenticator,
                                      create_obj, list_objs)

        # Cleanup
        acs.destroy()

    def test_authenticators_exists(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Exists
        create_obj = functools.partial(self._create_authenticator, direct=False)
        exists_obj = functools.partial(acs.authenticators_exists)
        self.helper_test_objects_exists(acs, accesscontrol.Authenticator,
                                        create_obj, exists_obj)

        # Cleanup
        acs.destroy()



        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Create
                                    create_obj)

        # Cleanup
        acs.destroy()


        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Get
                                      create_obj, get_obj)

        # Cleanup
        acs.destroy()


        # Create Server
        acs = self._create_accesscontrolserver()

        # Test List
                                      create_obj, list_objs)

        # Cleanup
        acs.destroy()


        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Exists
                                        create_obj, exists_obj)

        # Cleanup
        acs.destroy()

class AuthorizationTestCase(AccessControlTestCase, ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver()

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_authorization, direct=True)
        self.helper_test_obj_create(self.acs, accesscontrol.Authorization,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_authorization, direct=True)
        get_obj = functools.partial(accesscontrol.Authorization, self.acs, create=False)
        self.helper_test_obj_existing(self.acs, accesscontrol.Authorization,
                                      create_obj, get_obj)

    def test_clientuid(self):

        # Create Authorization
        clientuid = uuid.uuid4()
        auth = self._create_authorization(self.acs, direct=True, clientuid=clientuid)

        # Test Client UID
        self.assertEqual(auth.clientuid, clientuid)

        # Cleanup
        auth.destroy()

    def test_expiration(self):

        # Create Authorization
        expiration = time.time()
        auth = self._create_authorization(self.acs, direct=True, expiration=expiration)

        # Test Expriation
        self.assertEqual(auth.expiration, expiration)

        # Cleanup
        auth.destroy()

    def test_objperm(self):

        # Create Authorization
        objperm = 'TESTPERM2'
        auth = self._create_authorization(self.acs, direct=True, objperm=objperm)

        # Test Expriation
        self.assertEqual(auth.objperm, objperm)

        # Cleanup
        auth.destroy()

    def test_objtype(self):

        # Create Authorization
        objtype = 'TESTOBJ'
        auth = self._create_authorization(self.acs, direct=True, objtype=objtype)

        # Test Expriation
        self.assertEqual(auth.objtype, objtype)

        # Cleanup
        auth.destroy()

    def test_objuid(self):

        # Create Authorization
        objuid = uuid.uuid4()
        auth = self._create_authorization(self.acs, direct=True, objuid=objuid)

        # Test Expriation
        self.assertEqual(auth.objuid, objuid)

        # Cleanup
        auth.destroy()

    def test_status(self):

        # Create Authorization
        auth = self._create_authorization(self.acs, direct=True)

        # Test Status
        self.assertEqual(auth.status, accesscontrol._NEW_STATUS)

        # Cleanup
        auth.destroy()

class AuthenticatorTestCase(AccessControlTestCase, ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver()

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_authenticator, direct=True)
        self.helper_test_obj_create(self.acs, accesscontrol.Authenticator,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_authenticator, direct=True)
        get_obj = functools.partial(accesscontrol.Authenticator, self.acs, create=False)
        self.helper_test_obj_existing(self.acs, accesscontrol.Authenticator,
                                      create_obj, get_obj)

    def test_module(self):

        # Create Authenticator
        module = 'TESTMODULE'
        auth = self._create_authenticator(self.acs, direct=True, module=module)

        # Test Client UID
        self.assertEqual(auth.module, module)

        # Cleanup
        auth.destroy()


        # Create Authenticator
        actr = self._create_authenticator(self.acs, direct=True)

        # Test Empty

        for i in range(10):

        # Test Full


        # Test Empty

        # Cleanup
        actr.destroy()


        # Create Authenticator
        actr = self._create_authenticator(self.acs, direct=True)

        # Test Empty

        for i in range(10):

        # Test Full


        # Test Empty

        # Cleanup
        actr.destroy()


        # Create Authenticator
        actr = self._create_authenticator(self.acs, direct=True)

        # Test Empty

        for i in range(10):

        # Test Full


        # Test Empty

        # Cleanup
        actr.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
