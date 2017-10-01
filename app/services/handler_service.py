from os import path
from glob import glob
import yaml
import re
from pydash import _
from app import config
from distutils.dir_util import copy_tree
import shutil
import time
import os
import encode_service
import docker_service
from jinja2 import Environment, FileSystemLoader
from helper_service import (
    find_timestamp,
    get_unique_path
)
import sys

def get_handlers():
    handlers = {}
    for handler_path in glob(path.abspath(path.join(path.dirname(path.realpath(__file__)), '../', 'handlers', '*.yml'))):
        loader_path = re.sub(r'[^\/]+$', '', handler_path)
        matches = re.findall(r'[^\/]+$', handler_path)
        if len(matches) <= 0:
            exit('Houston, we have a problem')
        filename = matches[0]
        variables = {}
        dump = 'volback-unique-' + encode_service.str_encode(str(time.time()))
        with open(handler_path, 'r') as f:
            data = yaml.load(f)
            for key in _.keys(data):
                variables[key] = data[key]['variables'] if 'variables' in data[key] else {}
                variables[key]['dump_path'] = path.join(data[key]['data'], dump)
        env = Environment(loader=FileSystemLoader(loader_path), trim_blocks=True)
        template = env.get_template(filename)
        data = yaml.load(template.render(**variables))
        for key in _.keys(data):
            handlers[key] = {
                'data': data[key]['data'],
                'backup': data[key]['backup'],
                'restore': data[key]['restore'],
                'dump': dump
            }
    return handlers

def backup_mount(borg, mounts_path, container, mount, data_type, handlers=None, verbose=None):
    image = container['Config']['Image'].encode('utf8')
    mount_path = path.join(mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
    if not handlers:
        handlers = get_handlers()
    dump_path = path.join(mount_path, handlers[data_type]['dump'])
    sys.stdout.flush()
    timestamp = time.time()
    backup_name = encode_service.encode_backup_name(timestamp, mount['Destination'], image)
    if not path.isdir(mount_path):
        raise MountPathNotFound(mount_path)
    os.makedirs(dump_path)
    response = docker_service.execute(container['Id'], handlers[data_type]['backup'])
    if verbose:
        print('\n*****************')
        print(handlers[data_type]['backup'])
        print(response)
        print('*****************\n')
        sys.stdout.flush()
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

def restore_mount(borg, mounts_path, container, mount, data_type, handlers=None, restore_time=None, verbose=None):
    image = container['Config']['Image'].encode('utf8')
    mount_path = path.join(mounts_path, encode_service.str_encode(mount['Source'] + ':' + mount['Destination']))
    if not handlers:
        handlers = get_handlers()
    dump_path = path.join(mount_path, handlers[data_type]['dump'])
    timestamp = find_timestamp(restore_time, mount['Destination'], image, borg=borg)
    backup_name = encode_service.encode_backup_name(timestamp, mount['Destination'], image)
    extract_path = get_unique_path(mount_path)
    extract_from = borg.list(backup_name)[0]
    contents_path = path.join(extract_path, extract_from)
    os.makedirs(extract_path)
    os.makedirs(dump_path)
    borg.extract(backup_name, extract_path, extract_from)
    os.remove(path.join(contents_path, config.CONFIG_FILENAME))
    copy_tree(contents_path, dump_path)
    shutil.rmtree(extract_path)
    if verbose:
        response = docker_service.execute(container['Id'], handlers[data_type]['restore'])
        print('\n*****************')
        print(handlers[data_type]['restore'])
        print(response)
        print('*****************\n')
        sys.stdout.flush()
    shutil.rmtree(dump_path)
