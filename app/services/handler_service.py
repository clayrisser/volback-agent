from os import path
from glob import glob
import yaml
from pydash import _
from app import config
from distutils.dir_util import copy_tree
import shutil
import time
import os
import encode_service
from helper_service import (
    find_timestamp,
    get_unique_path
)

def get_handlers():
    handlers = {}
    for handler_path in glob(path.abspath(path.join(path.dirname(path.realpath(__file__)), '../', 'handlers', '*.yml'))):
        with open(handler_path, 'r') as f:
            data = yaml.load(f)
            for key in data:
                handlers[key] = data[key]
    return handlers

def backup_mount(borg, mounts_path, image, mount, data_type):
    mount_path = path.join(mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
    dump_path = get_unique_path(mount_path)
    timestamp = time.time()
    backup_name = encode_service.encode_backup_name(timestamp, mount['Destination'], image)
    if not path.isdir(mount_path):
        raise MountPathNotFound(mount_path)
    os.makedirs(dump_path)
    # dump to that folder
    with open(path.join(dump_path, config.CONFIG_FILENAME), 'w') as f:
        yaml.dump({
            'source': mount['Source'].encode('utf8'),
            'destination': mount['Destination'].encode('utf8'),
            'timestamp': timestamp,
            'data_type': 'raw',
            'image': image
        }, f, default_flow_style=False)
        borg.create(backup_name, dump_path)
        shutil.rmtree(dump_path)

def restore_mount(borg, mounts_path, image, mount, data_type, restore_time=None):
    mount_path = path.join(mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
    dump_path = get_unique_path(mount_path)
    timestamp = find_timestamp(restore_time, mount['Destination'], image, borg=borg)
    backup_name = encode_service.encode_backup_name(timestamp, mount['Destination'], image)
    extract_path = get_unique_path(mount_path)
    extract_from = borg.list(backup_name)[0]
    contents_path = path.join(extract_path, extract_from)
    os.makedirs(extract_path)
    os.makedirs(dump_path)
    borg.extract(backup_name, extract_path, extract_from)
    os.remove(path.join(contents_path, 'volback.yml'))
    copy_tree(contents_path, dump_path)
    shutil.rmtree(extract_path)
    # undump little folder to system
    shutil.rmtree(dump_path)
