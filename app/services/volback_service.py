import os
import shutil
from distutils.dir_util import copy_tree
import urllib
import re
import yaml
from bisect import bisect_left
from os import path
from borg_service import Borg
from docker_service import get_containers
import time

class Volback():
    def __init__(self, repo, passphrase=None, verbose=False, mount_path='/volumes'):
        repo = path.abspath(path.join(os.getcwd(), repo))
        if path.isfile(repo):
            exit('File exists where repo should be at ' + repo)
        self.repo = repo
        self.mount_path = mount_path
        self.passphrase = passphrase
        self.verbose = verbose

    def backup(self, container_ids=None, mount_destinations=None):
        borg = None
        if path.exists(self.repo):
            borg = Borg(self.repo, passphrase=self.passphrase, verbose=self.verbose)
        else:
            borg = Borg.init(self.repo, passphrase=self.passphrase, verbose=self.verbose)
        for container in get_containers(container_ids):
            for mount in container['Mounts']:
                if not mount_destinations:
                    data_type = 'raw'
                    image = container['Config']['Image']
                    timestamp = time.time()
                    backup_name_str = encode_backup_name(timestamp, mount['Destination'], image)
                    mount_location = self.mount_path + '/' + urllib.quote_plus(mount['Source'] + ':' + mount['Destination'])
                    with open(mount_location + '/volback.yml', 'w') as f:
                        config ={
                            'source': mount['Source'].encode('utf8'),
                            'destination': mount['Destination'].encode('utf8'),
                            'timestamp': timestamp,
                            'data_type': data_type,
                            'image': image.encode('utf8')
                        }
                        yaml.dump(config, f, default_flow_style=False)
                    borg.create(backup_name_str, mount_location)
                    os.remove(mount_location + '/volback.yml')

    def restore(self, container_ids=None, mount_destinations=False, restore_time=False):
        if not path.exists(self.repo):
            exit('Repo does not exist at ' + self.repo)
        borg = Borg(self.repo, passphrase=self.passphrase, verbose=self.verbose)
        for container in get_containers(container_ids):
            for mount in container['Mounts']:
                if not mount_destinations:
                    image = container['Config']['Image']
                    timestamp = find_timestamp(restore_time, mount['Destination'], image, borg=borg)
                    if not timestamp:
                        continue
                    backup_name_str = encode_backup_name(timestamp, mount['Destination'], image)
                    mount_location = self.mount_path + '/' + urllib.quote_plus(mount['Source'] + ':' + mount['Destination'])
                    tmp_location = path.join(self.mount_path, 'tmp')
                    extract_path = path.abspath((tmp_location + '/' + mount_location).replace('//', '/').replace('//', '/'))
                    extract_from = borg.list(backup_name_str)[0]
                    extract_to = path.abspath(path.join(extract_path, extract_from))
                    if not path.exists(extract_path):
                        os.makedirs(extract_path)
                    borg.extract(backup_name_str, extract_path, extract_from)
                    os.remove(path.join(extract_to, 'volback.yml'))
                    copy_tree(extract_to, mount_location)
                    shutil.rmtree(tmp_location)

class BackupName():
    def __init__(self, timestamp, destination, image):
        self.timestamp = timestamp
        self.destination = destination
        self.image = image

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

def decode_backup_name(backup_name_str):
    timestamp = None
    destination = None
    image = None
    backup_name_str = urllib.unquote_plus(backup_name_str)
    matches = re.findall(r'^[^\|]+', backup_name_str)
    if len(matches) > 0:
        timestamp = float(matches[0])
    matches = re.findall(r'(?<=\|).+(?=\|)', backup_name_str)
    if len(matches) > 0:
        destination = urllib.unquote_plus(matches[0])
    matches = re.findall(r'[^\|]+$', backup_name_str)
    if len(matches) > 0:
        image = urllib.unquote_plus(matches[0])
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
    return urllib.quote_plus(str(timestamp) + '|' + urllib.quote_plus(destination) + '|' + urllib.quote_plus(image))
