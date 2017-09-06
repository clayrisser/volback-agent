import os
from os import path

class Borg():

    def __init__(self, repo_path, verbose=False):
        self.path = path.abspath(path.join(os.getcwd(), repo_path))
        self.verbose = verbose

    @staticmethod
    def init(repo_path, encryption=None):
        self = Borg(repo_path)
        self.system('init', path.abspath(path.join(os.getcwd(), repo_path)))
        return self

    def create(self, backup_location, backup_name):
        return self.system(
            'create',
            '--list ::' + backup_name + ' ' + path.abspath(path.join(os.getcwd(), backup_location))
        )

    def extract(self):
        pass

    def check(self):
        pass

    def rename(self):
        pass

    def list(self):
        pass

    def delete(self):
        pass

    def prune(self):
        pass

    def info(self):
        pass

    def mount(self):
        pass

    def unmount(self):
        pass

    def keyExport(self):
        pass

    def keyImport(self):
        pass

    def changePassphrase(self):
        pass

    def serve(self):
        pass

    def upgrade(self):
        pass

    def breakLock(self):
        pass

    def system(self, command, args=''):
        os.environ['BORG_REPO'] = path.abspath(path.join(os.getcwd(), self.path))
        return os.popen('borg ' + command + (' -v' if self.verbose else '') + ' ' + args).read()
