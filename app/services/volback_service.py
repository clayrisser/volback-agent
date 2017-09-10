import os
import shutil
from distutils.dir_util import copy_tree
import base64
import re
import yaml
from bisect import bisect_left
from os import path
from borg_service import Borg
from docker_service import get_containers
import time

class Volback():
    def __init__(self, repo, passphrase=None, verbose=False, mounts_path='/volumes'):
        repo = path.abspath(path.join(os.getcwd(), repo))
        if path.isfile(repo):
            exit('File exists where repo should be at ' + repo)
        self.repo = repo
        self.mounts_path = mounts_path
        self.passphrase = passphrase
        self.verbose = verbose
        self.config_filename = 'volback.yml'

    def backup(self, container_ids=None, mount_destinations=None):
        for container in get_containers(container_ids):
            for mount in container['Mounts']:
                if not mount_destinations:
                    service_name = container['Name'][1:]
                    self.backup_mount(service_name, container, mount)

    def restore(self, container_ids=None, mount_destinations=False, restore_time=False):
        for container in get_containers(container_ids):
            for mount in container['Mounts']:
                if not mount_destinations:
                    service_name = container['Name'][1:]
                    self.restore_mount(service_name, container, mount)

    def backup_mount(self, service_name, container, mount):
        mount_path = path.join(self.mounts_path, str_encode(mount['Source'] + ':' + mount['Destination']))
        backup_path = path.join(self.repo, service_name, str_encode(mount['Destination']))
        borg = None
        if path.exists(backup_path):
            borg = Borg(backup_path, passphrase=self.passphrase, verbose=self.verbose)
        else:
            borg = Borg.init(backup_path, passphrase=self.passphrase, verbose=self.verbose)
        data_type = 'raw'
        image = container['Config']['Image'].encode('utf8')
        timestamp = time.time()
        backup_name = encode_backup_name(timestamp, mount['Destination'], image)
        with open(path.join(mount_path, self.config_filename), 'w') as f:
            yaml.dump({
                'source': mount['Source'].encode('utf8'),
                'destination': mount['Destination'].encode('utf8'),
                'timestamp': timestamp,
                'data_type': data_type,
                'image': image
            }, f, default_flow_style=False)
            borg.create(backup_name, mount_path)
            os.remove(path.join(mount_path, self.config_filename))

    def restore_mount(self, service_name, container, mount, restore_time=None):
        mount_path = path.join(self.mounts_path, str_encode(mount['Source'] + ':' + mount['Destination']))
        backup_path = path.join(self.repo, service_name, str_encode(mount['Destination']))
        if not path.exists(backup_path):
            print('Backup does not exist for mount \'' + mount['Destination'] + '\' in service \'' + service_name + '\'')
            return
        borg = Borg(backup_path, passphrase=self.passphrase, verbose=self.verbose)
        data_type = 'raw'
        image = container['Config']['Image'].encode('utf8')
        timestamp = find_timestamp(restore_time, mount['Destination'], image, borg=borg)
        backup_name = encode_backup_name(timestamp, mount['Destination'], image)
        extract_path = get_extract_path(mount_path)
        extract_from = borg.list(backup_name)[0]
        contents_path = path.join(extract_path, extract_from)
        if not path.exists(extract_path):
            os.makedirs(extract_path)
        borg.extract(backup_name, extract_path, extract_from)
        os.remove(path.join(contents_path, 'volback.yml'))
        copy_tree(contents_path, mount_path)
        shutil.rmtree(extract_path)

def get_extract_path(backup_path):
    extract_path = path.join(backup_path, str_encode(str(time.time())))
    if path.exists(extract_path):
        extract_path = find_extract_path(backup_path)
    return extract_path

def find_timestamp(restore_time, destination, image, borg):
    timestamp = time.time()
    if restore_time:
        timestamp = time.mktime(dateparser.parse(restore_time).timetuple())
    timestamps = list()
    for backup_name_str in borg.list():
        backup_name = decode_backup_name(backup_name_str)
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

class BackupName():
    def __init__(self, timestamp, destination, image):
        self.timestamp = timestamp
        self.destination = destination
        self.image = image

def decode_backup_name(backup_name_str):
    timestamp = None
    destination = None
    image = None
    backup_name_str = str_decode(backup_name_str)
    matches = re.findall(r'^[^\|]+', backup_name_str)
    if len(matches) > 0:
        timestamp = float(matches[0])
    matches = re.findall(r'(?<=\|).+(?=\|)', backup_name_str)
    if len(matches) > 0:
        destination = str_decode(matches[0])
    matches = re.findall(r'[^\|]+$', backup_name_str)
    if len(matches) > 0:
        image = str_decode(matches[0])
    return BackupName(
        timestamp=timestamp,
        destination=destination,
        image=image
    )

def encode_backup_name(poly, destination=None, image=None):
    backup_name = None
    timestamp = None
    if not image and not destination:
        backup_name = poly
        timestamp = backup_name.timestamp
        destination = backup_name.destination
        image = backup_name.image
    else:
        timestamp = poly
    return str_encode(str(timestamp) + '|' + str_encode(destination) + '|' + str_encode(image))

def str_encode(string):
    return base64.b64encode(string).replace('=', '')

def str_decode(string):
    return base64.b64decode(string + ('=' * (-len(string) % 4)))
