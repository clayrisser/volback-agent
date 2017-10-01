import os
import base64
import re
import sys
from os import path
from borg_service import Borg
from docker_service import get_services, valid_mount
from pydash import _
import handler_service
from app.exceptions.volback_exceptions import (
    FileExistsAtRepo,
    MountPathNotFound
)
from app.exceptions.docker_exceptions import (
    ContainerIdsNotFound
)
import raw_service
import encode_service

class Volback():
    def __init__(self, repo, passphrase=None, verbose=False, mounts_path='/volumes'):
        repo = path.abspath(path.join(os.getcwd(), repo))
        if path.isfile(repo):
            raise FileExistsAtRepo(repo)
        self.repo = repo
        self.mounts_path = mounts_path
        self.passphrase = passphrase
        self.verbose = verbose
        self.handlers = handler_service.get_handlers()

    def backup(self, container_ids=None, mount_destinations=None):
        valid_mounts = self.get_valid_mounts(container_ids, mount_destinations)
        if len(valid_mounts) <= 0:
            print('No valid mounts to backup')
        for valid_mount in valid_mounts:
            self.backup_mount(valid_mount['service_name'], valid_mount['container'], valid_mount['mount'])

    def restore(self, container_ids=None, mount_destinations=False, restore_time=False, restore_all=False):
        if not restore_all and not container_ids:
            raise ContainerIdsNotFound()
        valid_mounts = self.get_valid_mounts(container_ids, mount_destinations)
        if len(valid_mounts) <= 0:
            print('No valid mounts to backup')
        for valid_mount in valid_mounts:
            self.restore_mount(valid_mount['service_name'], valid_mount['container'], valid_mount['mount'])

    def get_valid_mounts(self, container_ids=None, mount_destinations=None):
        valid_mounts = list()
        for service in get_services(container_ids):
            for mount in service.container['Mounts']:
                if not valid_mount(mount):
                    continue
                if mount_destinations:
                    valid = False
                    for mount_destination in mount_destinations:
                        if trim_path(mount['Destination']) == trim_path(mount_destination):
                            valid = True
                    if not valid:
                        if self.verbose:
                            print('Skipping ' + mount['Destination'])
                        continue
                valid_mounts.append({
                    'service_name': service.name,
                    'container': service.container,
                    'mount': mount
                })
        return valid_mounts

    def backup_mount(self, service_name, container, mount):
        mount_path = path.join(self.mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
        backup_path = path.join(self.repo, service_name, encode_service.str_encode(mount['Destination']))
        borg = None
        if path.exists(backup_path):
            borg = Borg(backup_path, passphrase=self.passphrase, verbose=self.verbose)
        else:
            borg = Borg.init(backup_path, passphrase=self.passphrase, verbose=self.verbose)
        data_type = self.get_data_type(container)
        image = container['Config']['Image'].encode('utf8')
        if data_type == 'raw':
            return raw_service.backup_mount(borg, self.mounts_path, image, mount)
        return handler_service.backup_mount(borg, self.mounts_path, image, mount, data_type)

    def restore_mount(self, service_name, container, mount, restore_time=None):
        mount_path = path.join(self.mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
        backup_path = path.join(self.repo, service_name, encode_service.str_encode(mount['Destination']))
        if not path.exists(backup_path):
            print('Backup does not exist for mount \'' + mount['Destination'] + '\' in service \'' + service_name + '\'')
            return
        borg = Borg(backup_path, passphrase=self.passphrase, verbose=self.verbose)
        data_type = self.get_data_type(container)
        image = container['Config']['Image'].encode('utf8')
        if data_type == 'raw':
            return raw_service.restore_mount(borg, self.mounts_path, image, mount, restore_time)
        return handler_service.restore_mount(borg, self.mounts_path, image, mount, data_type, restore_time=restore_time)

    def get_data_type(self, container):
        data_type = container['Config']['Image'][:container['Config']['Image'].index(':')]
        if not _.includes(_.keys(self.handlers), data_type):
            data_type = 'raw'
        return data_type

def trim_path(path):
    return re.sub(r'(^\/)|(\/$)', '', path)
