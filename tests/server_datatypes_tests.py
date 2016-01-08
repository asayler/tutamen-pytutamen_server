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

## Tests Common ##
import tests_common

## pcollections ##
from pcollections import collections
from pcollections import abc_base

## tutamen_server ##
from pytutamen_server import datatypes


### Function Classes ###

class FunctionsTestCase(tests_common.BaseTestCase):

    def test_build_pkey(self):

        base_key = "test_base_key"
        prefix = "prefix"
        postfix = "postfix"
        sep = "_"

        # Test Base
        key = datatypes.build_pkey(base_key)
        self.assertEqual(key, base_key)

        # Test Prefix
        key = datatypes.build_pkey(base_key, prefix=prefix)
        self.assertEqual(key, (prefix + sep + base_key))

        # Test Postfix
        key = datatypes.build_pkey(base_key, postfix=postfix)
        self.assertEqual(key, (base_key + sep + postfix))

        # Test All
        key = datatypes.build_pkey(base_key, prefix=prefix, postfix=postfix)
        self.assertEqual(key, (prefix + sep + base_key + sep + postfix))

    def test_check_isinstance(self):

        # Test Fail
        self.assertRaises(TypeError, datatypes.check_isinstance, 1, str)

        # Test Pass
        datatypes.check_isinstance("test", str)

    def test_check_issubclass(self):

        class substr(str):
            pass

        # Test Fail
        self.assertRaises(TypeError, datatypes.check_issubclass, object, str)

        # Test Pass
        datatypes.check_issubclass(substr, str)

    def test_nos(self):

        self.assertEqual(datatypes.nos(None), None)
        self.assertEqual(datatypes.nos("test"), "test")
        self.assertEqual(datatypes.nos(1), str(1))

### Object Classes ###

class PersistentObjectTestCase(tests_common.BaseTestCase):

    def test_init(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)
        self.assertIsInstance(obj, datatypes.PersistentObject)

    def test_pbackend(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Test Pbackend
        self.assertEqual(obj.pbackend, self.pbackend)

    def test_pcollections(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Test Pcollections
        self.assertIsInstance(obj.pcollections, collections.PCollections)

    def test_key(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Test key
        self.assertEqual(obj.key, key)

    def test_prefix(self):

        # Create Obj
        key = "test_obj"
        prefix = "test_prefix"
        obj = datatypes.PersistentObject(self.pbackend, key, prefix=prefix)

        # Test prefix
        self.assertEqual(obj.prefix, prefix)

    def test_repr(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Test repr
        self.assertEqual(repr(obj), "{:s}_{:s}".format("PersistentObject", key))

    def test_hash(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Test hash
        self.assertEqual(hash(obj), hash(key))

    def test_eq(self):

        # Create Objs
        key_1 = "test_obj_1"
        key_2 = "test_obj_2"
        obj_a = datatypes.PersistentObject(self.pbackend, key_1)
        obj_b = datatypes.PersistentObject(self.pbackend, key_1)
        obj_c = datatypes.PersistentObject(self.pbackend, key_2)

        # Test equal
        self.assertEqual(obj_a, obj_b)

        # Test Not Equal
        self.assertNotEqual(obj_a, obj_c)
        self.assertNotEqual(obj_a, key_1)

    def test_build_pkey(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Build Key
        postfix = "test_postfix"
        pkey = obj._build_pkey(postfix=postfix)
        self.assertEqual(pkey, datatypes.build_pkey(obj.key, prefix=obj.prefix, postfix=postfix))

    def test_build_pobj(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Build Obj
        postfix = "test_postfix"
        pobj = obj._build_pobj(obj.pcollections.String, postfix, create="")
        self.assertIsInstance(pobj, abc_base.String)

        # Cleanup
        pobj.rem()

    def test_val_to_key(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Test Str
        key = "test_string"
        val = key
        self.assertEqual(obj.val_to_key(val), key)

        # Test UUID
        key = "eb424026-6f54-4ef8-a4d0-bb658a1fc6cf"
        val = uuid.UUID(key)
        self.assertEqual(obj.val_to_key(val), key)

        # Test Object
        key = "test_object"
        val = datatypes.PersistentObject(self.pbackend, key=key)
        self.assertEqual(obj.val_to_key(val), key)

        # Test Bad Type
        self.assertRaises(TypeError, obj.val_to_key, None)

    def test_val_to_uid(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Test UUID
        uid = uuid.uuid4()
        val = uid
        self.assertEqual(obj.val_to_uid(val), uid)

        # Test Str
        val = "eb424026-6f54-4ef8-a4d0-bb658a1fc6cf"
        uid = uuid.UUID(val)
        self.assertEqual(obj.val_to_uid(val), uid)

        # Test Object
        uid = uuid.uuid4()
        val = datatypes.UUIDObject(self.pbackend, uid=uid)
        self.assertEqual(obj.val_to_uid(val), uid)

        # Test Bad Type
        self.assertRaises(TypeError, obj.val_to_uid, None)

    def test_val_to_obj(self):

        # Create Obj
        key = "test_obj"
        obj = datatypes.PersistentObject(self.pbackend, key)

        # Test Object
        sub = datatypes.PersistentObject(self.pbackend, key="test_obj")
        val = obj
        self.assertEqual(obj.val_to_obj(val, datatypes.PersistentObject), sub)

        # Test Str
        val = "test_obj"
        sub = datatypes.PersistentObject(self.pbackend, key=val)
        self.assertEqual(obj.val_to_obj(val, datatypes.PersistentObject), sub)

        # Test UUID
        val = uuid.uuid4()
        sub = datatypes.UUIDObject(self.pbackend, uid=val)
        self.assertEqual(obj.val_to_obj(val, datatypes.UUIDObject), sub)

        # Test Bad Type
        self.assertRaises(TypeError, obj.val_to_obj, None, datatypes.PersistentObject)

class UUIDObjectTestCase(tests_common.BaseTestCase):

    def test_init_create(self):

        # Test Bad Key String
        key = "BadUUIDStr"
        self.assertRaises(ValueError, datatypes.UUIDObject,
                          self.pbackend, key=key, create=True)

        # Test Bad UID
        uid = "NotUUIDObj"
        self.assertRaises(TypeError, datatypes.UUIDObject,
                          self.pbackend, uid=uid, create=True)

        # Test Create Object w/ Random UUID
        obj = datatypes.UUIDObject(self.pbackend, create=True)
        self.assertIsInstance(obj, datatypes.UUIDObject)

        # Test Create Object w/ UUID String
        key = "eb424026-6f54-4ef8-a4d0-bb658a1fc6cf"
        obj = datatypes.UUIDObject(self.pbackend, key=key, create=True)
        self.assertIsInstance(obj, datatypes.UUIDObject)
        self.assertEqual(obj.key, key)

        # Test Create Object w/ UUID Object
        uid = uuid.uuid4()
        obj = datatypes.UUIDObject(self.pbackend, uid=uid, create=True)
        self.assertIsInstance(obj, datatypes.UUIDObject)
        self.assertEqual(obj.uid, uid)

    def test_init_existing(self):

        # Test Bad Key String
        key = "BadUUIDStr"
        self.assertRaises(ValueError, datatypes.UUIDObject,
                          self.pbackend, key=key, create=False)

        # Test Bad UID
        uid = "NotUUIDObj"
        self.assertRaises(TypeError, datatypes.UUIDObject,
                          self.pbackend, uid=uid, create=False)

        # Test No Key or UID
        self.assertRaises(TypeError, datatypes.UUIDObject,
                          self.pbackend, create=False)

        # Create Object
        obj = datatypes.UUIDObject(self.pbackend, create=True)
        key = obj.key
        uid = obj.uid

        # Test Existing (via key)
        obj = datatypes.UUIDObject(self.pbackend, key=key, create=False)
        self.assertIsInstance(obj, datatypes.UUIDObject)
        self.assertEqual(obj.key, key)

        # Test Existing (via uid)
        obj = datatypes.UUIDObject(self.pbackend, uid=uid, create=False)
        self.assertIsInstance(obj, datatypes.UUIDObject)
        self.assertEqual(obj.uid, uid)

    def test_uuid(self):

        # Create Object
        obj = datatypes.UUIDObject(self.pbackend, create=True)

        # Test UUID
        self.assertEqual(str(obj.uid), obj.key)

class UserDataObjectTestCase(tests_common.BaseTestCase):

    def test_init_create(self):

        # Test Bad Data Type
        key = "TestUserDataObject"
        self.assertRaises(TypeError, datatypes.UserDataObject,
                          self.pbackend, create=True, key=key, userdata=None)

        # Test Create Object
        key = "TestUserDataObject"
        userdata = {"key1": "val1", "key2": "val2", "key3": "val3"}
        obj = datatypes.UserDataObject(self.pbackend, create=True, key=key,
                                           userdata=userdata)
        self.assertIsInstance(obj, datatypes.UserDataObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_existing(self):

        # Create Object
        key = "TestUserDataObject"
        obj = datatypes.UserDataObject(self.pbackend, key=key, create=True)


        # Test Existing
        obj = datatypes.UserDataObject(self.pbackend, key=key, create=False)
        self.assertIsInstance(obj, datatypes.UserDataObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_userdata(self):

        # Create Object
        key = "TestUserDataObject"
        userdata = {"key1": "val1", "key2": "val2", "key3": "val3"}
        obj = datatypes.UserDataObject(self.pbackend, create=True, key=key,
                                                          userdata=userdata)

        # Test userdata
        self.assertEqual(obj.userdata, userdata)

        # Cleanup
        obj.destroy()

class ServerObjectTestCase(tests_common.BaseTestCase):

    def test_init_and_destroy(self):

        # Create Server
        key = "test_server"
        srv = datatypes.ServerObject(self.pbackend, key=key)
        self.assertIsInstance(srv, datatypes.ServerObject)

        # Cleanup
        srv.destroy()

class ChildObjectTestCase(tests_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.parent = datatypes.PersistentObject(self.pbackend, key="TestParent")
        self.pindex = datatypes.ChildIndex(self.parent, datatypes.ChildObject, "TestChildren")

    def tearDown(self):

        # Teardown Properties
        self.pindex.destroy()
        self.parent.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create_and_destroy(self):

        # Test Bad Index Type
        key = "TestChild"
        self.assertRaises(TypeError, datatypes.ChildObject,
                          self.pbackend, pindex=None, create=True, key=key)

        # Test Create Object
        key = "TestChild"
        obj = datatypes.ChildObject(self.pbackend, pindex=self.pindex, create=True, key=key)
        self.assertIsInstance(obj, datatypes.ChildObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_existing_and_destroy(self):

        # Test Fail
        key = "TestChild"
        self.assertRaises(datatypes.ObjectDNE, datatypes.ChildObject, self.pbackend,
                          pindex=self.pindex, key=key, create=False)

        # Create Object
        obj = datatypes.ChildObject(self.pbackend, pindex=self.pindex, key=key, create=True)

        # Test Existing (create=False)
        obj = datatypes.ChildObject(self.pbackend, pindex=self.pindex, key=key, create=False)
        self.assertIsInstance(obj, datatypes.ChildObject)
        self.assertEqual(obj.key, key)

        # Test Existing (create=True)
        obj = datatypes.ChildObject(self.pbackend, pindex=self.pindex, key=key, create=True)
        self.assertIsInstance(obj, datatypes.ChildObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_pindex(self):

        # Create Object
        key = "TestChild"
        obj = datatypes.ChildObject(self.pbackend, pindex=self.pindex, key=key, create=True)

        # Test Pindex
        self.assertEqual(obj.pindex, self.pindex)

        # Cleanup
        obj.destroy()

    def test_parent(self):

        # Create Object
        key = "TestChild"
        obj = datatypes.ChildObject(self.pbackend, pindex=self.pindex, key=key, create=True)

        # Test Parent
        self.assertEqual(obj.parent, self.parent)

        # Cleanup
        obj.destroy()

    def test_exists(self):

        # Create Object
        key = "TestChild"
        obj = datatypes.ChildObject(self.pbackend, pindex=self.pindex, key=key, create=True)

        # Test Exists
        self.assertTrue(obj.exists())

        # Cleanup
        obj.destroy()

        # Test DNE
        self.assertFalse(obj.exists())

class ChildIndexTestCase(tests_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.parent = datatypes.PersistentObject(self.pbackend, key="TestParent")

    def tearDown(self):

        # Teardown Properties
        self.parent.destroy()

        # Call Parent
        super().tearDown()

    def test_init_and_destroy(self):

        # Test Bad Parent Type
        self.assertRaises(TypeError, datatypes.ChildIndex,
                          None, datatypes.ChildObject, "TestChildIndex")

        # Test Bad Child Type
        self.assertRaises(TypeError, datatypes.ChildIndex,
                          self.parent, None, "TestChildIndex")

        # Test Bad Label
        self.assertRaises(TypeError, datatypes.ChildIndex,
                          self.parent, datatypes.ChildObject, None)

        # Test Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)
        self.assertIsInstance(idx, datatypes.ChildIndex)

        # Cleanup
        idx.destroy()

    def test_parent(self):

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)

        # Test Parent
        self.assertEqual(idx.parent, self.parent)

        # Cleanup
        idx.destroy()

    def test_type_child(self):

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)

        # Test Parent
        self.assertEqual(idx.type_child, datatypes.ChildObject)

        # Cleanup
        idx.destroy()

    def test_create(self):

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)

        # Creat Child
        key = "test_child"
        child = idx.create(key=key)
        self.assertIsInstance(child, datatypes.ChildObject)
        self.assertEqual(child.key, key)

        # Cleanup
        child.destroy()
        idx.destroy()

    def test_len(self):

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)

        # Confirm Empty
        self.assertEqual(len(idx), 0)

        # Creat Children
        children = set()
        for i in range(10):
            key = "child_{}".format(i)
            child = idx.create(key=key)
            children.add(child)

        # Confirm Full
        self.assertEqual(len(idx), 10)

        # Delete Children
        for child in children:
            child.destroy()

        # Confirm Empty
        self.assertEqual(len(idx), 0)

        # Cleanup
        idx.destroy()

    def test_get(self):

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)

        # Creat Child
        key = "test_child"
        idx.create(key=key)

        # Get Child
        child = idx.get(key=key)
        self.assertIsInstance(child, datatypes.ChildObject)
        self.assertEqual(child.key, key)

        # Cleanup
        child.destroy()
        idx.destroy()

    def test_exists(self):

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)
        key = "test_child"

        # Test DNE
        self.assertFalse(idx.exists(key))

        # Creat Child
        child = idx.create(key=key)

        # Test Exists
        self.assertTrue(idx.exists(key))

        # Cleanup
        child.destroy()
        idx.destroy()

    def test_by_key(self):

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)

        # Creat Children
        children = set()
        keys = set()
        for i in range(10):
            key = "child_{}".format(i)
            child = idx.create(key=key)
            keys.add(key)
            children.add(child)

        # Test by_key
        self.assertEqual(idx.by_key(), keys)

        # Cleanup
        for child in children:
            child.destroy()
        idx.destroy()

    def test_by_uid(self):

        class UUIDChild(datatypes.ChildObject, datatypes.UUIDObject):
            pass

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, UUIDChild, label)

        # Creat Children
        children = set()
        uids = set()
        for i in range(10):
            uid = uuid.uuid4()
            child = idx.create(uid=uid)
            uids.add(uid)
            children.add(child)

        # Test by_uid
        self.assertEqual(idx.by_uid(), uids)

        # Cleanup
        for child in children:
            child.destroy()
        idx.destroy()

    def test_by_obj(self):

        # Create Index
        label = "TestChildIndex"
        idx = datatypes.ChildIndex(self.parent, datatypes.ChildObject, label)

        # Creat Children
        children = set()
        for i in range(10):
            key = "child_{}".format(i)
            child = idx.create(key=key)
            children.add(child)

        # Test by_key
        self.assertEqual(idx.by_obj(), children)

        # Cleanup
        for child in children:
            child.destroy()
        idx.destroy()

class MasterTestObj(datatypes.UUIDObject):

    def __init__(self, pbackend, **kwargs):
        """Initialize Master Test Object"""

        # Call Parent
        super().__init__(pbackend, **kwargs)

        # Setup Master Index
        def slave_gen(key):
            return SlaveTestObj(pbackend, key=key).masters
        self.slaves = datatypes.MasterObjIndex(self, "slaves", slave_gen, SlaveTestObj)

    def destroy(self):

        # Cleanup Index
        self.slaves.destroy()

        # Call Parent
        super().destroy()

class SlaveTestObj(datatypes.UUIDObject):

    def __init__(self, pbackend, **kwargs):
        """Initialize Slave Test Object"""

        # Call Parent
        super().__init__(pbackend, **kwargs)

        # Setup Master Index
        def master_gen(key):
            return MasterTestObj(pbackend, key=key).slaves
        self.masters = datatypes.SlaveObjIndex(self, "masters", master_gen, MasterTestObj)

    def destroy(self):

        # Cleanup Index
        self.masters.destroy()

        # Call Parent
        super().destroy()

class ObjectIndexTestCase(tests_common.BaseTestCase):

    def test_init_and_destroy(self):

        obj = datatypes.PersistentObject(self.pbackend, key="test_obj", create=True)

        # Test Bad Parent Type
        self.assertRaises(TypeError, datatypes.MasterObjIndex,
                          None, "TestMasterIndex", bool, SlaveTestObj)
        self.assertRaises(TypeError, datatypes.SlaveObjIndex,
                          None, "TestSlaveIndex", bool, MasterTestObj)

        # Test Bad Label Type
        self.assertRaises(TypeError, datatypes.MasterObjIndex,
                          obj, None, bool, SlaveTestObj)
        self.assertRaises(TypeError, datatypes.SlaveObjIndex,
                          obj, None, bool, MasterTestObj)

        # Test Bad Generator Type
        self.assertRaises(TypeError, datatypes.MasterObjIndex,
                          obj, "TestMasterIndex", None, SlaveTestObj)
        self.assertRaises(TypeError, datatypes.SlaveObjIndex,
                          obj, "TestSlaveIndex", None, MasterTestObj)

        # Test Bad Member Type
        self.assertRaises(TypeError, datatypes.MasterObjIndex,
                          obj, "TestMasterIndex", bool, None)
        self.assertRaises(TypeError, datatypes.SlaveObjIndex,
                          obj, "TestSlaveIndex", bool, None)

        obj.destroy()

        # Test Create Master Index
        master = MasterTestObj(self.pbackend, create=True)
        self.assertIsInstance(master.slaves, datatypes.MasterObjIndex)
        master.destroy()

        # Test Create Slave Index
        slave = SlaveTestObj(self.pbackend, create=True)
        self.assertIsInstance(master.slaves, datatypes.MasterObjIndex)
        slave.destroy()

    def test_obj(self):

        # Create Indexed Objects
        master = MasterTestObj(self.pbackend, create=True)
        slave = SlaveTestObj(self.pbackend, create=True)

        # Test Object
        self.assertEqual(master.slaves.obj, master)
        self.assertEqual(slave.masters.obj, slave)

        # Cleanup
        slave.destroy()
        master.destroy()

    def test_type_member(self):

        # Create Indexed Objects
        master = MasterTestObj(self.pbackend, create=True)
        slave = SlaveTestObj(self.pbackend, create=True)

        # Test type_member
        self.assertEqual(master.slaves.type_member, SlaveTestObj)
        self.assertEqual(slave.masters.type_member, MasterTestObj)

        # Cleanup
        slave.destroy()
        master.destroy()

    def test_add_rem_len_ismember_master(self):

        # Create Master
        master = MasterTestObj(self.pbackend, create=True)

        # Create Slaves
        slaves = set()
        for i in range(10):
            slave = SlaveTestObj(self.pbackend, create=True)
            slaves.add(slave)

        # Add Bad Obj
        self.assertRaises(TypeError, master.slaves.add, None)

        # Add Slaves by Obj
        self.assertEqual(len(master.slaves), 0)
        for slave in slaves:
            master.slaves.add(slave)
            self.assertTrue(master.slaves.ismember(slave))

        # Remove Slaves by Obj
        self.assertEqual(len(master.slaves), 10)
        for slave in slaves:
            master.slaves.remove(slave)
            self.assertFalse(master.slaves.ismember(slave))

        # Add Slaves by Key
        self.assertEqual(len(master.slaves), 0)
        for slave in slaves:
            master.slaves.add(slave.key)
            self.assertTrue(master.slaves.ismember(slave.key))

        # Remove Slaves by Key
        self.assertEqual(len(master.slaves), 10)
        for slave in slaves:
            master.slaves.remove(slave.key)
            self.assertFalse(master.slaves.ismember(slave.key))

        # Add Slaves by UID
        self.assertEqual(len(master.slaves), 0)
        for slave in slaves:
            master.slaves.add(slave.uid)
            self.assertTrue(master.slaves.ismember(slave.uid))

        # Remove Slaves by UID
        self.assertEqual(len(master.slaves), 10)
        for slave in slaves:
            master.slaves.remove(slave.uid)
            self.assertFalse(master.slaves.ismember(slave.uid))

        # Cleanup
        for slave in slaves:
            slave.destroy()
        master.destroy()

    def test_len_ismember_slave(self):

        # Create Master
        slave = SlaveTestObj(self.pbackend, create=True)

        # Create Slaves
        masters = set()
        for i in range(10):
            master = MasterTestObj(self.pbackend, create=True)
            masters.add(master)

        # Add Masters by Obj
        self.assertEqual(len(slave.masters), 0)
        for master in masters:
            master.slaves.add(slave)
            self.assertTrue(slave.masters.ismember(master))

        # Remove Masters by Obj
        self.assertEqual(len(slave.masters), 10)
        for master in masters:
            master.slaves.remove(slave)
            self.assertFalse(slave.masters.ismember(master))

        # Add Masters by Key
        self.assertEqual(len(slave.masters), 0)
        for master in masters:
            master.slaves.add(slave.key)
            self.assertTrue(slave.masters.ismember(master.key))

        # Remove Masters by Key
        self.assertEqual(len(slave.masters), 10)
        for master in masters:
            master.slaves.remove(slave.key)
            self.assertFalse(slave.masters.ismember(master.key))

        # Add Masters by UID
        self.assertEqual(len(slave.masters), 0)
        for master in masters:
            master.slaves.add(slave.uid)
            self.assertTrue(slave.masters.ismember(master.uid))

        # Remove Masters by UID
        self.assertEqual(len(slave.masters), 10)
        for master in masters:
            master.slaves.remove(slave.uid)
            self.assertFalse(slave.masters.ismember(master.uid))

        # Cleanup
        for master in masters:
            master.destroy()
        slave.destroy()

    def test_by_key_master(self):

        # Create Master
        master = MasterTestObj(self.pbackend, create=True)

        # Test Empty
        self.assertEqual(master.slaves.by_key(), set())

        # Create and Add Slaves
        keys = set()
        slaves = set()
        for i in range(10):
            slave = SlaveTestObj(self.pbackend, create=True)
            slaves.add(slave)
            master.slaves.add(slave)
            keys.add(slave.key)

        # Test Full
        self.assertEqual(master.slaves.by_key(), keys)

        # Cleanup Slaves
        for slave in slaves:
            slave.destroy()

        # Test Empty
        self.assertEqual(master.slaves.by_key(), set())

        # Cleanup Master
        master.destroy()

    def test_by_key_slave(self):

        # Create Master
        slave = SlaveTestObj(self.pbackend, create=True)

        # Test Empty
        self.assertEqual(slave.masters.by_key(), set())

        # Create and Add Slaves
        keys = set()
        masters = set()
        for i in range(10):
            master = MasterTestObj(self.pbackend, create=True)
            masters.add(master)
            master.slaves.add(slave)
            keys.add(master.key)

        # Test Full
        self.assertEqual(slave.masters.by_key(), keys)

        # Cleanup Masters
        for master in masters:
            master.destroy()

        # Test Empty
        self.assertEqual(slave.masters.by_key(), set())

        # Cleanup Slave
        slave.destroy()

    def test_by_uid_master(self):

        # Create Master
        master = MasterTestObj(self.pbackend, create=True)

        # Test Empty
        self.assertEqual(master.slaves.by_uid(), set())

        # Create and Add Slaves
        uids = set()
        slaves = set()
        for i in range(10):
            slave = SlaveTestObj(self.pbackend, create=True)
            slaves.add(slave)
            master.slaves.add(slave)
            uids.add(slave.uid)

        # Test Full
        self.assertEqual(master.slaves.by_uid(), uids)

        # Cleanup Slaves
        for slave in slaves:
            slave.destroy()

        # Test Empty
        self.assertEqual(master.slaves.by_uid(), set())

        # Cleanup Master
        master.destroy()

    def test_by_uid_slave(self):

        # Create Master
        slave = SlaveTestObj(self.pbackend, create=True)

        # Test Empty
        self.assertEqual(slave.masters.by_uid(), set())

        # Create and Add Slaves
        uids = set()
        masters = set()
        for i in range(10):
            master = MasterTestObj(self.pbackend, create=True)
            masters.add(master)
            master.slaves.add(slave)
            uids.add(master.uid)

        # Test Full
        self.assertEqual(slave.masters.by_uid(), uids)

        # Cleanup Masters
        for master in masters:
            master.destroy()

        # Test Empty
        self.assertEqual(slave.masters.by_uid(), set())

        # Cleanup Slave
        slave.destroy()

    def test_by_obj_master(self):

        # Create Master
        master = MasterTestObj(self.pbackend, create=True)

        # Test Empty
        self.assertEqual(master.slaves.by_obj(), set())

        # Create and Add Slaves
        slaves = set()
        for i in range(10):
            slave = SlaveTestObj(self.pbackend, create=True)
            slaves.add(slave)
            master.slaves.add(slave)

        # Test Full
        self.assertEqual(master.slaves.by_obj(), slaves)

        # Cleanup Slaves
        for slave in slaves:
            slave.destroy()

        # Test Empty
        self.assertEqual(master.slaves.by_obj(), set())

        # Cleanup Master
        master.destroy()

    def test_by_obj_slave(self):

        # Create Master
        slave = SlaveTestObj(self.pbackend, create=True)

        # Test Empty
        self.assertEqual(slave.masters.by_obj(), set())

        # Create and Add Slaves
        masters = set()
        for i in range(10):
            master = MasterTestObj(self.pbackend, create=True)
            masters.add(master)
            master.slaves.add(slave)

        # Test Full
        self.assertEqual(slave.masters.by_obj(), masters)

        # Cleanup Masters
        for master in masters:
            master.destroy()

        # Test Empty
        self.assertEqual(slave.masters.by_obj(), set())

        # Cleanup Slave
        slave.destroy()

class IndexTestCase(tests_common.BaseTestCase):

    def test_init_create(self):

        # Create Index
        key = "test_index"
        index = datatypes.Index(self.pbackend, key=key, create=True)
        self.assertIsInstance(index, datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_init_existing(self):

        # Create Index
        key = "test_index"
        datatypes.Index(self.pbackend, key=key, create=True)
        index = datatypes.Index(self.pbackend, key=key, create=False)
        self.assertIsInstance(index, datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_members(self):

        # Create Index
        key = "test_index"
        index = datatypes.Index(self.pbackend, key=key, create=True)

        # Create Object
        key = "test_object"
        obj = datatypes.PersistentObject(self.pbackend, key=key)

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
        index = datatypes.Index(self.pbackend, key=key, create=True)

        # Create Object
        key = "test_object"
        obj = datatypes.PersistentObject(self.pbackend, key=key)

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
        index = datatypes.Index(self.pbackend, key=key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_indexed_obj_{}".format(i)
            objs.append(datatypes.PersistentObject(self.pbackend, key=key))

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
        index = datatypes.Index(self.pbackend, key=key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_object_{}".format(i)
            obj = datatypes.PersistentObject(self.pbackend, key=key)
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
        index = datatypes.Index(self.pbackend, key=key, create=True)

        # Create Objects
        objs = []
        for i in range(10):
            key = "test_object_{}".format(i)
            obj = datatypes.PersistentObject(self.pbackend, key=key)
            objs.append(obj)
            index.add(obj)

        # Test Destroy
        index.destroy()

        # Cleanup
        for obj in objs:
            obj.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
