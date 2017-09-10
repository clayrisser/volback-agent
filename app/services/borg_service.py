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
        repo_path = path.abspath(path.join(os.getcwd(), repo_path))
        pipe_list = None
        pargs = {
            'verbose': self.verbose
        }
        if passphrase:
            pipe_list = [
                'echo ' + passphrase,
                'echo ' + passphrase,
                'echo'
            ]
        if not passphrase:
            pargs['encryption'] = 'none'
        self.command(
            'init',
            pargs,
            path=repo_path,
            pipe_list=pipe_list
        )
        return self

    def create(self, backup_name, backup_location):
        backup_location = path.abspath(path.join(os.getcwd(), backup_location))
        return self.command(
            'create',
            {
                'verbose': self.verbose,
                'list': True
            },
            backup_name=backup_name,
            path=backup_location
        )

    def extract(self, backup_name, extract_location, extract_from):
        return self.command(
            'extract',
            {'verbose': self.verbose},
            backup_name=backup_name,
            path=extract_from,
            working_dir=extract_location
        )

    def check(self):
        pass

    def rename(self):
        pass

    def list(self, backup_name=None):
        response = None
        if backup_name:
            response = self.command('list', {
                'verbose': self.verbose,
                'short': True
            }, backup_name).split('\n')
        else:
            response = self.command('list', {
                'verbose': self.verbose,
                'short': True
            }).split('\n')
        return response[:len(response) - 1]

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

    def command(self, command, pargs=None, backup_name=None, path=None, working_dir=None, pipe_list=None):
        if pargs:
            for parg, value in pargs.iteritems():
                command += encode_parg_str(parg, value)
        if backup_name:
            command += ' ::' + backup_name
        if path:
            command += ' ' + path
        return self.system(command, pipe_list, working_dir)

    def system(self, command, pipe_list=None, working_dir=None):
        cwd = None
        if working_dir:
            cwd = os.getcwd()
            os.chdir(working_dir)
        os.environ['BORG_REPO'] = path.abspath(path.join(os.getcwd(), self.path))
        if self.passphrase:
            os.environ['BORG_PASSPHRASE'] = self.passphrase
        elif 'BORG_PASSPHRASE' in os.environ:
            del os.environ['BORG_PASSPHRASE']
        command = 'borg ' + command
        if pipe_list:
            pipe = '('
            for item in pipe_list:
                pipe += item + '; '
            pipe = pipe[:len(pipe) - 2] + ') | '
            command = pipe + command
        if 'DEBUG' in os.environ and os.environ['DEBUG'].lower() == 'true':
            print('$ ' + command + '\n')
        response = os.popen(command).read()
        if working_dir:
            os.chdir(cwd)
        return response

def encode_parg_str(parg, value):
    if value == None:
        return ''
    parg_str = '-'
    if len(parg) > 1:
        parg_str += '-'
    parg_str += parg
    if type(value) == bool:
        if value:
            return ' ' + parg_str
        else:
            return ''
    elif type(value) == str:
        return ' ' + parg_str + '=' + value
    else:
        return ' ' + parg_str + '=' + str(value)
