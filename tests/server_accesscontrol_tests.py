#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Access Control Tests


### Imports ###

## stdlib ##
import uuid
import unittest

# Tests Common
import server_common

## tutamen_server ##
import tutamen_server.accesscontrol

### Object Classes ###

class AccessControlServerTestCase(server_common.BaseTestCase):

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

    def test_init_and_destroy(self):

        # Create Server
        acs = tutamen_server.accesscontrol.AccessControlServer(self.driver)
        self.assertIsInstance(acs, tutamen_server.accesscontrol.AccessControlServer)

        # Cleanup
        acs.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
