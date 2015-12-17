#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Datatypes Tests


### Imports ###

## stdlib ##
import uuid
import unittest

# Tests Common
import tests_common

## tutamen_server ##
from pytutamen_server import datatypes


### Function Classes ###

class FunctionsTestCase(tests_common.BaseTestCase):

    def test_build_key(self):

        base_key = "test_base_key"
        prefix = "prefix"
        postfix = "postfix"
        sep = "_"

        # Test Base
        key = datatypes.build_key(base_key)
        self.assertEqual(key, base_key)

        # Test Prefix
        key = datatypes.build_key(base_key, prefix=prefix)
        self.assertEqual(key, (prefix + sep + base_key))

        # Test Postfix
        key = datatypes.build_key(base_key, postfix=postfix)
        self.assertEqual(key, (base_key + sep + postfix))

        # Test All
        key = datatypes.build_key(base_key, prefix=prefix, postfix=postfix)
        self.assertEqual(key, (prefix + sep + base_key + sep + postfix))

    def test_check_isinstance(self):

        # Test Fail
        self.assertRaises(TypeError, datatypes.check_isinstance, 1, str)

        # Test Pass
        datatypes.check_isinstance("test", str)

### Object Classes ###

class PersistentObjectServerTestCase(tests_common.BaseTestCase):

    def test_init_and_destroy(self):

        # Create Server
        srv = datatypes.PersistentObjectServer(self.driver)
        self.assertIsInstance(srv, datatypes.PersistentObjectServer)

        # Cleanup
        srv.destroy()

    def test_driver(self):

        # Create Server
        srv = datatypes.PersistentObjectServer(self.driver)

        # Test Driver
        self.assertIs(srv.driver, self.driver)

        # Cleanup
        srv.destroy()

    def test_objects(self):

        # Create Server
        srv = datatypes.PersistentObjectServer(self.driver)
        objs = []

        # Test Empty
        self.assertEqual(len(srv.objects), len(objs))

        # Add Objects
        for i in range(10):
            key = "test_object_{}".format(i)
            objs.append(datatypes.PersistentObject(srv, key=key, create=True))

        # Test Populated
        self.assertEqual(len(srv.objects), len(objs))

        # Cleanup
        for obj in objs:
            obj.destroy()
        srv.destroy()

    def test_exists(self):

        # Create Server
        srv = datatypes.PersistentObjectServer(self.driver)
        objs = []

        # Add Objects
        for i in range(10):
            key = "test_object_{}".format(i)
            objs.append(datatypes.PersistentObject(srv, key=key, create=True))

        # Test Exists
        for obj in objs:
            self.assertTrue(srv.exists(obj.key))

        # Cleanup Objects
        for obj in objs:
            obj.destroy()

        # Test DNE
        for obj in objs:
            self.assertFalse(srv.exists(obj.key))

        # Cleanup
        srv.destroy()

class PersistentObjectBasis(tests_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.srv = datatypes.PersistentObjectServer(self.driver)

    def tearDown(self):

        # Teardown Properties
        self.srv.destroy()

        # Call Parent
        super().tearDown()

class PersistentObjectTestCase(PersistentObjectBasis):

    def test_init_create_new(self):

        # Test No Key
        self.assertRaises(TypeError, datatypes.PersistentObject, self.srv)

        # Test DNE
        key = "test_object"
        self.assertRaises(datatypes.ObjectDNE,
                          datatypes.PersistentObject,
                          self.srv, key=key, create=False)

        # Test Create Object
        obj = datatypes.PersistentObject(self.srv, key=key, create=True)
        self.assertIsInstance(obj, datatypes.PersistentObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_create_existing(self):

        # Create Object
        key = "test_object"
        datatypes.PersistentObject(self.srv, key=key, create=True)
        obj = datatypes.PersistentObject(self.srv, key=key, create=True)
        self.assertIsInstance(obj, datatypes.PersistentObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_create_overwrite(self):

        # Create Object
        key = "test_object"
        datatypes.PersistentObject(self.srv, key=key, create=True)
        obj = datatypes.PersistentObject(self.srv, key=key, create=True, overwrite=True)
        self.assertIsInstance(obj, datatypes.PersistentObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_existing(self):

        # Create Object
        key = "test_object"
        datatypes.PersistentObject(self.srv, key=key, create=True)
        obj = datatypes.PersistentObject(self.srv, key=key, create=False)
        self.assertIsInstance(obj, datatypes.PersistentObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_exists(self):

        # Create Object
        key = "test_object"
        obj = datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test Exists
        self.assertTrue(obj.exists())

        # Cleanup
        obj.destroy()

        # Test DNE
        self.assertFalse(obj.exists())

    def test_key(self):

        # Create Object
        key = "test_object"
        obj = datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test key
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_srv(self):

        # Create Object
        key = "test_object"
        obj = datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test key
        self.assertEqual(obj.srv, self.srv)

        # Cleanup
        obj.destroy()

    def test_destroy(self):

        # Create Object
        key = "test_object"
        obj = datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test Destroy
        obj.destroy()
        self.assertFalse(obj.exists())
        self.assertFalse(self.srv.exists(obj.key))

class UUIDObjectTestCase(PersistentObjectBasis):

    def test_init_new(self):

        # Test Bad Key Type
        key = "NotValidUUID"
        self.assertRaises(ValueError, datatypes.UUIDObject,
                          self.srv, key=key)

        # Test Create Object
        obj = datatypes.UUIDObject(self.srv, create=True)
        self.assertIsInstance(obj, datatypes.UUIDObject)

        # Cleanup
        obj.destroy()

    def test_init_existing(self):

        # Create Object
        obj = datatypes.UUIDObject(self.srv, create=True)
        key = obj.key
        uid = obj.uid

        # Test Existing (via key)
        obj = datatypes.UUIDObject(self.srv, key=key, create=True)
        self.assertIsInstance(obj, datatypes.UUIDObject)
        self.assertEqual(obj.key, key)
        self.assertEqual(obj.uid, uid)

        # Test Existing (via uid)
        obj = datatypes.UUIDObject(self.srv, uid=uid, create=True)
        self.assertIsInstance(obj, datatypes.UUIDObject)
        self.assertEqual(obj.key, key)
        self.assertEqual(obj.uid, uid)

        # Cleanup
        obj.destroy()

    def test_uuid(self):

        # Create Object
        obj = datatypes.UUIDObject(self.srv, create=True)

        # Test UUID
        self.assertEqual(str(obj.uid), obj.key)

        # Cleanup
        obj.destroy()

class UserMetadataObjectTestCase(PersistentObjectBasis):

    def test_init_new(self):

        # Test Bad Metadata Type
        key = "TestUserMetadataObject"
        usermetadata = "NotValidMetadataType"
        self.assertRaises(TypeError, datatypes.UserMetadataObject,
                          self.srv, cretae=True, key=key, usermetadata=usermetadata)

        # Test Create Object
        key = "TestUserMetadataObject"
        usermetadata = {"key1": "val1", "key2": "val2", "key3": "val3"}
        obj = datatypes.UserMetadataObject(self.srv, create=True, key=key,
                                                          usermetadata=usermetadata)
        self.assertIsInstance(obj, datatypes.UserMetadataObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_existing(self):

        # Create Object
        key = "TestUserMetadataObject"
        obj = datatypes.UserMetadataObject(self.srv, key=key, create=True)


        # Test Existing
        obj = datatypes.UserMetadataObject(self.srv, key=key, create=True)
        self.assertIsInstance(obj, datatypes.UserMetadataObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_usermetadata(self):

        # Create Object
        key = "TestUserMetadataObject"
        usermetadata = {"key1": "val1", "key2": "val2", "key3": "val3"}
        obj = datatypes.UserMetadataObject(self.srv, create=True, key=key,
                                                          usermetadata=usermetadata)

        # Test usermetadata
        self.assertEqual(obj.usermetadata, usermetadata)

        # Cleanup
        obj.destroy()

class IndexTestCase(PersistentObjectBasis):

    def test_init_create_new(self):

        # Create Index
        key = "test_index"
        index = datatypes.Index(self.srv, key=key, create=True)
        self.assertIsInstance(index, datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_init_create_existing(self):

        # Create Index
        key = "test_index"
        datatypes.Index(self.srv, key=key, create=True)
        index = datatypes.Index(self.srv, key=key, create=True)
        self.assertIsInstance(index, datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_init_existing(self):

        # Create Index
        key = "test_index"
        datatypes.Index(self.srv, key=key, create=True)
        index = datatypes.Index(self.srv, key=key, create=False)
        self.assertIsInstance(index, datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_members(self):

        # Create Index
        key = "test_index"
        index = datatypes.Index(self.srv, key=key, create=True)

        # Create Object
        key = "test_object"
        obj = datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test Members - Empty
        self.assertEqual(len(index.members), 0)

        # Add Member
        index.add(obj)

        # Test Members - Non-empty
        self.assertEqual(len(index.members), 1)

        # Cleanup
        obj.destroy()
        index.destroy()

    def test_is_member(self):

        # Create Index
        key = "test_index"
        index = datatypes.Index(self.srv, key=key, create=True)

        # Create Object
        key = "test_object"
        obj = datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test is_member() - False
        self.assertFalse(index.is_member(obj.key))

        # Add Member
        index.add(obj)

        # Test is_member() - True
        self.assertTrue(index.is_member(obj.key))

        # Cleanup
        obj.destroy()
        index.destroy()

    def test_add(self):

        # Create Index
        key = "test_index"
        index = datatypes.Index(self.srv, key=key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_indexed_obj_{}".format(i)
            objs.append(datatypes.PersistentObject(self.srv, key=key, create=True))

        # Test Add
        cnt = 0
        for obj in objs:
            cnt += 1
            index.add(obj)
            self.assertIn(obj.key, index.members)
            self.assertEqual(len(index.members), cnt)

        # Cleanup
        index.destroy()
        for obj in objs:
            obj.destroy()

    def test_remove(self):

        # Create Index
        key = "test_index"
        index = datatypes.Index(self.srv, key=key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_object_{}".format(i)
            obj = datatypes.PersistentObject(self.srv, key=key, create=True)
            objs.append(obj)
            index.add(obj)

        # Test Remove
        cnt = len(index.members)
        for obj in objs:
            cnt -= 1
            index.remove(obj)
            self.assertNotIn(obj.key, index.members)
            self.assertEqual(len(index.members), cnt)

        # Cleanup
        index.destroy()
        for obj in objs:
            obj.destroy()

    def test_destroy(self):

        # Create Index
        key = "test_index"
        index = datatypes.Index(self.srv, key=key, create=True)

        # Create Objects
        objs = []
        for i in range(10):
            key = "test_object_{}".format(i)
            obj = datatypes.PersistentObject(self.srv, key=key, create=True)
            objs.append(obj)
            index.add(obj)

        # Test Destroy
        index.destroy()
        self.assertFalse(index.exists())

        # Cleanup
        for obj in objs:
            obj.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
