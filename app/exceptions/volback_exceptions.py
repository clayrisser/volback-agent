from exceptions import BaseException

class FileExistsAtRepo(BaseException):
    known = True
    def __init__(self, repo):
        self.payload = {
            'repo': repo
        }
        self.message = 'File exists where repo should be at ' + repo

class MountPathNotFound(BaseException):
    known = True
    def __init__(self, mount_path):
        self.payload = {
            'mount_path': mount_path
        }
        self.message = 'Mount path \'' + mount_path + '\' not found'

class RepoPathNotFound(BaseException):
    known = True
    def __init__(self, repo_path=None):
        self.payload = {
            'repo_path': repo_path
        }
        self.message = 'Repo path not found'
        if repo_path:
            self.message = 'Repo path \'' + repo_path + '\' not found'
