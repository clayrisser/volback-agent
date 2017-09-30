from exceptions import BaseException

class ContainerNotFound(BaseException):
    known = True
    def __init__(self, container_name):
        self.payload = {
            'container_name': container_name
        }
        self.message = 'Container \'' + container_name + '\' not found'

class ContainerIdsNotFound(BaseException):
    known = True
    def __init__(self, container_ids=None):
        self.payload = {
            'container_ids': container_ids
        }
        self.message = 'Container ids not found'
        if container_ids:
            self.message = 'Container ids \'' + ','.join(container_ids.join) + '\' not found'
