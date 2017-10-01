from app import config
from distutils.dir_util import copy_tree
import shutil
from os import path
from bisect import bisect_left
import time
import os
import yaml
import encode_service

def backup_mount(borg, mounts_path, image, mount):
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
        borg.create(backup_name, mount_path)
        os.remove(path.join(mount_path, config.CONFIG_FILENAME))

def restore_mount(borg, mounts_path, image, mount, restore_time=None):
    mount_path = path.join(mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
    timestamp = find_timestamp(restore_time, mount['Destination'], image, borg=borg)
    backup_name = encode_service.encode_backup_name(timestamp, mount['Destination'], image)
    extract_path = get_extract_path(mount_path)
    extract_from = borg.list(backup_name)[0]
    contents_path = path.join(extract_path, extract_from)
    if not path.exists(extract_path):
        os.makedirs(extract_path)
    borg.extract(backup_name, extract_path, extract_from)
    os.remove(path.join(contents_path, 'volback.yml'))
    copy_tree(contents_path, mount_path)
    shutil.rmtree(extract_path)

def find_timestamp(restore_time, destination, image, borg):
    timestamp = time.time()
    if restore_time:
        timestamp = time.mktime(dateparser.parse(restore_time).timetuple())
    timestamps = list()
    for backup_name_str in borg.list():
        backup_name = encode_service.decode_backup_name(backup_name_str)
        if backup_name.image == image and backup_name.destination == destination:
            timestamps.append(backup_name.timestamp)
    if len(timestamps) <= 0:
        return None
    return closest_timestamp(timestamps, timestamp)

def closest_timestamp(timestamps, timestamp):
    pos = bisect_left(timestamps, timestamp)
    if pos == 0:
        return timestamps[0]
    if pos == len(timestamps):
        return timestamps[-1]
    before = timestamps[pos - 1]
    after = timestamps[pos]
    if after - timestamp < timestamp - before:
        return after
    return before

def get_extract_path(backup_path):
    extract_path = path.join(backup_path, encode_service.str_encode(str(time.time())))
    if path.exists(extract_path):
        extract_path = find_extract_path(backup_path)
    return extract_path
