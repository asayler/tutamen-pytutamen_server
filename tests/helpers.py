# -*- coding: utf-8 -*-


# Andy Sayler
# 2015, 2016
# Tutamen Server Tests
# Helper Functions


### Imports ###

## stdlib ##
import uuid

## tutamen_server ##
from pytutamen_server import datatypes


### Helper Classes ###

class ObjectsHelpers(object):

    def helper_test_obj_create(self, obj_type, obj_index, create_obj,
                               uuidobj=True, permobj=False):

        # Test Create (Random)
        obj = create_obj()
        self.assertIsInstance(obj, obj_type)
        self.assertTrue(obj.exists())
        self.assertTrue(obj_index.exists(obj))

        # Test OE
        self.assertRaises(datatypes.ObjectExists, create_obj, key=obj.key)
        if uuidobj:
            self.assertRaises(datatypes.ObjectExists, create_obj, uid=obj.uid)
        elif permobj:
            self.assertRaises(datatypes.ObjectExists, create_obj,
                              objtype=obj.objtype, objuid=obj.objuid)
        else:
            raise Exception("Requires either uuidobj or permobj")

        # Cleanup
        obj.destroy()

        # Test Create (Key)
        if uuidobj:
            key = "eb424026-6f54-4ef8-a4d0-bb658a1fc6cf"
        elif permobj:
            key = "testobj_eb424026-6f54-4ef8-a4d0-bb658a1fc6cf"
        else:
            raise Exception("Requires either uuidobj or permobj")
        obj = create_obj(key=key)
        self.assertIsInstance(obj, obj_type)
        self.assertTrue(obj.exists())
        self.assertTrue(obj_index.exists(obj))
        self.assertEqual(obj.key, key)
        obj.destroy()

        if uuidobj:
            # Test Create (uid)
            uid = uuid.uuid4()
            obj = create_obj(uid=uid)
            self.assertIsInstance(obj, obj_type)
            self.assertTrue(obj.exists())
            self.assertTrue(obj_index.exists(obj))
            self.assertEqual(obj.uid, uid)
            obj.destroy()
        elif permobj:
            # Test Create (objuid)
            objuid = uuid.uuid4()
            obj = create_obj(objuid=objuid)
            self.assertIsInstance(obj, obj_type)
            self.assertTrue(obj.exists())
            self.assertTrue(obj_index.exists(obj))
            self.assertEqual(obj.objuid, objuid)
            obj.destroy()
        else:
            raise Exception("Requires either uuidobj or permobj")

    def helper_test_obj_existing(self, obj_type, obj_index, create_obj, get_obj,
                                 uuidobj=True, permobj=False):

        # Test DNE
        if uuidobj:
            uid = uuid.uuid4()
            self.assertRaises(datatypes.ObjectDNE, get_obj, uid=uid)
        elif permobj:
            objtype = "nosuchtype"
            objuid = uuid.uuid4()
            self.assertRaises(datatypes.ObjectDNE, get_obj, objuid=objuid, objtype=objtype)
        else:
            raise Exception("Requires either uuidobj or permobj")

        # Create Object
        obj = create_obj()

        # Test get (key)
        key = obj.key
        obj = get_obj(key=key)
        self.assertIsInstance(obj, obj_type)
        self.assertTrue(obj.exists())
        self.assertTrue(obj_index.exists(obj))
        self.assertEqual(obj.key, key)

        if uuidobj:
            # Test get (uid)
            uid = obj.uid
            obj = get_obj(uid=uid)
            self.assertIsInstance(obj, obj_type)
            self.assertTrue(obj.exists())
            self.assertTrue(obj_index.exists(obj))
            self.assertEqual(obj.uid, uid)
        elif permobj:
            # Test get (objuid)
            objtype = obj.objtype
            objuid = obj.objuid
            obj = get_obj(objtype=objtype, objuid=objuid)
            self.assertIsInstance(obj, obj_type)
            self.assertTrue(obj.exists())
            self.assertTrue(obj_index.exists(obj))
            self.assertEqual(obj.objuid, objuid)
        else:
            raise Exception("Requires either uuidobj or permobj")

        # Cleanup
        obj.destroy()

    def helper_test_master_obj_index(self, create_master, create_slave,
                                     get_master_index):

        # Create Master Obj
        master = create_master()

        # Test Empty
        self.assertEqual(len(get_master_index(master)), 0)
        self.assertEqual(get_master_index(master).by_obj(), set())

        # Create Slaves
        slaves = set()
        for i in range(10):
            slave = create_slave()
            slaves.add(slave)

        # Add Slaves
        for slave in slaves:
            get_master_index(master).add(slave)
            self.assertTrue(get_master_index(master).ismember(slave))

        # Test Full
        self.assertEqual(len(get_master_index(master)), 10)
        self.assertEqual(get_master_index(master).by_obj(), slaves)

        # Remove some slaves
        rem_slaves = set()
        for slave in slaves:
            get_master_index(master).remove(slave)
            self.assertFalse(get_master_index(master).ismember(slave))
            rem_slaves.add(slave)
            if len(rem_slaves) >= 5:
                break
        self.assertEqual(len(get_master_index(master)), 5)
        self.assertEqual(get_master_index(master).by_obj(), (slaves - rem_slaves))

        # Cleanup Slaves
        for slave in slaves:
            slave.destroy()

        # Test Empty
        self.assertEqual(len(get_master_index(master)), 0)
        self.assertEqual(get_master_index(master).by_obj(), set())

        # Cleanup
        master.destroy()

    def helper_test_slave_obj_index(self, create_master, create_slave,
                                    get_master_index, get_slave_index):

        # Create Slave Obj
        slave = create_slave()

        # Test Empty
        self.assertEqual(len(get_slave_index(slave)), 0)
        self.assertEqual(get_slave_index(slave).by_obj(), set())

        # Create Master
        masters = set()
        for i in range(10):
            master = create_master()
            masters.add(master)

        # Add Masters
        for master in masters:
            get_master_index(master).add(slave)
            self.assertTrue(get_slave_index(slave).ismember(master))

        # Test Full
        self.assertEqual(len(get_slave_index(slave)), 10)
        self.assertEqual(get_slave_index(slave).by_obj(), masters)

        # Remove some masters
        rem_masters = set()
        for master in masters:
            get_master_index(master).remove(slave)
            self.assertFalse(get_slave_index(slave).ismember(master))
            rem_masters.add(master)
            if len(rem_masters) >= 5:
                break
        self.assertEqual(len(get_slave_index(slave)), 5)
        self.assertEqual(get_slave_index(slave).by_obj(), (masters - rem_masters))

        # Cleanup Masters
        for master in masters:
            master.destroy()

        # Test Empty
        self.assertEqual(len(get_slave_index(slave)), 0)
        self.assertEqual(get_slave_index(slave).by_obj(), set())

        # Cleanup
        slave.destroy()

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
