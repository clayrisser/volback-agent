import os
from os import path

class Borg():
    def __init__(self, repo_path, passphrase=None, verbose=False):
        self.path = path.abspath(path.join(os.getcwd(), repo_path))
        self.passphrase = passphrase
        self.verbose = verbose

    @staticmethod
    def init(repo_path, passphrase=None, verbose=False):
        self = Borg(repo_path, passphrase=passphrase, verbose=verbose)
        command = None
        if passphrase:
            command = '(echo ' + passphrase + '; echo ' + passphrase + '; echo) | ';
        command = 'borg init '
        if not passphrase:
            command += ' --encryption=none'
        command += (' -v' if self.verbose else '') + ' ' + path.abspath(path.join(os.getcwd(), repo_path))
        os.system(command)
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
        if self.passphrase:
            os.environ['BORG_PASSPHRASE'] = self.passphrase
        elif 'BORG_PASSPHRASE' in os.environ:
            del os.environ['BORG_PASSPHRASE']
        return os.popen('borg ' + command + (' -v' if self.verbose else '') + ' ' + args).read()
