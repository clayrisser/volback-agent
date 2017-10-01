from app import config
import sys
from distutils.dir_util import copy_tree
import shutil
from os import path
import time
import os
import yaml
import encode_service
from helper_service import (
    find_timestamp,
    get_unique_path
)

def backup_mount(borg, mounts_path, container, mount):
    image = container['Config']['Image'].encode('utf8')
    mount_path = path.join(mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
    timestamp = time.time()
    backup_name = encode_service.encode_backup_name(timestamp, mount['Destination'], image)
    if not path.isdir(mount_path):
        raise MountPathNotFound(mount_path)
    with open(path.join(mount_path, config.CONFIG_FILENAME), 'w') as f:
        yaml.dump({
            'source': mount['Source'].encode('utf8'),
            'destination': mount['Destination'].encode('utf8'),
            'timestamp': timestamp,
            'data_type': 'raw',
            'image': image
        }, f, default_flow_style=False)
    sys.stdout.flush()
    borg.create(backup_name, mount_path)
    os.remove(path.join(mount_path, config.CONFIG_FILENAME))

def restore_mount(borg, mounts_path, container, mount, restore_time=None):
    image = container['Config']['Image'].encode('utf8')
    mount_path = path.join(mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
    timestamp = find_timestamp(restore_time, mount['Destination'], image, borg=borg)
    backup_name = encode_service.encode_backup_name(timestamp, mount['Destination'], image)
    extract_path = get_unique_path(mount_path)
    extract_from = borg.list(backup_name)[0]
    contents_path = path.join(extract_path, extract_from)
    if not path.exists(extract_path):
        os.makedirs(extract_path)
    borg.extract(backup_name, extract_path, extract_from)
    os.remove(path.join(contents_path, config.CONFIG_FILENAME))
    copy_tree(contents_path, mount_path)
    shutil.rmtree(extract_path)
