import unittest
from distutils.dir_util import copy_tree
import os
import app
from app.services import (
    volback_service,
    encode_service,
    handler_service
)
from os import makedirs
from os import path

Volback = volback_service.Volback
TestCase = unittest.TestCase

class TestVolbackService(TestCase):

    def setUp(self):
        self.repo = '/backup'
        self.volback = Volback(self.repo, passphrase=None, verbose=True)
        self.container_ids = ['some-mongo', 'some-alpine']
        self.mount_destinations = None

    def test_volback_service(self):
        self.assertIsNotNone(volback_service)

    def test_backup(self):
        for valid_mount in self.volback.get_valid_mounts(self.container_ids, self.mount_destinations):
            mount = valid_mount['mount']
            mount_path = path.join(self.volback.mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
            if not path.exists(self.volback.mounts_path):
                makedirs(self.volback.mounts_path)
            if not path.exists(mount_path):
                handlers = handler_service.get_handlers()
                data_type = self.volback.get_data_type(valid_mount['container'])
                if data_type != 'raw' and volback_service.trim_path(handlers[data_type]['data']) == volback_service.trim_path(mount['Destination']):
                    os.symlink(mount['Source'], mount_path)
                else:
                    os.makedirs(mount_path)
                    copy_tree(mount['Source'], mount_path)
        self.volback.backup(self.container_ids, self.mount_destinations)
        self.assertTrue(True)

    def test_restore(self):
        self.test_backup()
        self.volback.restore(self.container_ids, self.mount_destinations)
        self.assertTrue(True)

    def test_get_valid_mounts(self):
        valid_mounts = self.volback.get_valid_mounts(self.container_ids, self.mount_destinations)
        self.assertEqual(len(valid_mounts), 3)
        self.assertEqual(valid_mounts[0]['service_name'], 'some-mongo')
        self.assertIsInstance(valid_mounts[0]['container'], dict)

    def test_backup_mount(self):
        valid_mount = self.volback.get_valid_mounts(['some-mongo'], ['/data/db'])[0]
        mount = valid_mount['mount']
        mount_path = path.join(self.volback.mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
        if not path.exists(self.volback.mounts_path):
            makedirs(self.volback.mounts_path)
        if not path.exists(mount_path):
            handlers = handler_service.get_handlers()
            data_type = self.volback.get_data_type(valid_mount['container'])
            if data_type != 'raw' and volback_service.trim_path(handlers[data_type]['data']) == volback_service.trim_path(mount['Destination']):
                os.symlink(mount['Source'], mount_path)
            else:
                os.makedirs(mount_path)
                copy_tree(mount['Source'], mount_path)
        self.volback.backup_mount(valid_mount['service_name'], valid_mount['container'], mount)
        self.assertTrue(True)

    def test_restore_mount(self):
        self.test_backup()
        valid_mount = self.volback.get_valid_mounts(['some-mongo'], ['/data/db'])[0]
        mount = valid_mount['mount']
        mount_path = path.join(self.volback.mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
        if not path.exists(self.volback.mounts_path):
            makedirs(self.volback.mounts_path)
        if not path.exists(mount_path):
            handlers = handler_service.get_handlers()
            data_type = self.volback.get_data_type(valid_mount['container'])
            if data_type != 'raw' and volback_service.trim_path(handlers[data_type]['data']) == volback_service.trim_path(mount['Destination']):
                os.symlink(mount['Source'], mount_path)
            else:
                os.makedirs(mount_path)
                copy_tree(mount['Source'], mount_path)
        self.volback.restore_mount(valid_mount['service_name'], valid_mount['container'], mount)
        self.assertTrue(True)

    def test_get_data_type(self):
        container = self.volback.get_valid_mounts(['some-mongo'], ['/data/db'])[0]['container']
        data_type = self.volback.get_data_type(container)
        self.assertEqual(data_type, 'mongo')

def main():
    unittest.main(module=__name__, exit=False)

if __name__ == '__main__':
    main()
