import os
import urllib
import re
from os import path
from borg_service import Borg
from docker_service import get_mounts
import time

class Volback():
    def __init__(self, repo, passphrase=None, verbose=False, mount_path='/volumes'):
        self.repo = path.abspath(path.join(os.getcwd(), repo))
        self.mount_path = mount_path
        self.passphrase = passphrase
        self.verbose = verbose

    def backup(self, container_ids=None):
        borg = None
        if path.exists(self.repo):
            if path.isfile(self.repo):
                exit('File exists where repo should be')
            borg = Borg(self.repo, passphrase=self.passphrase, verbose=self.verbose)
        else:
            borg = Borg.init(self.repo, passphrase=self.passphrase, verbose=self.verbose)
        mounts = get_mounts(container_ids)
        for mount in mounts:
            backup_name = str(time.time()) + urllib.quote_plus(mount['Source']) + '_raw'
            mount_location = self.mount_path + '/' + urllib.quote_plus(mount['Source']) + '_raw'
            borg.create(mount_location, backup_name)

    def restore(self, container_ids=None):
        pass
