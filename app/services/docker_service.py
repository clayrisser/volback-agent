import docker
import pydash as _
from app.exceptions.docker_exceptions import (
    ContainerNotFound
)

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

ignore_mounts = {
    'sources': [
        '/var/lib/docker'
    ]
}

def get_service(service_id):
    service_name = None
    container = None
    if type(service_id) == str:
        service = service_id.split(':')
        service_name = service[0]
        if len(service) >= 2:
            service_name = service[1]
        try:
            container = client.containers.get(service[0]).attrs
        except docker.errors.NotFound:
            raise ContainerNotFound(service[0])
    else: # prevents getting container 2x for get_services
        container = service_id
        service_name = container['Name'][1:]
    return Service(service_name, container)

def execute(container_id, cmd, stdout=True, stderr=True, stdin=True, privileged=False):
    container = client.containers.get(container_id)
    return container.exec_run(cmd, stdout=stdout, stderr=stderr, stdin=stdin, privileged=privileged)

def get_services(container_ids):
    services = list()
    if container_ids:
        for container_id in container_ids:
            services.append(get_service(container_id))
    else:
        for container in client.containers.list():
            services.append(get_service(container.attrs))
    return services

def valid_mount(mount):
    for source in ignore_mounts['sources']:
        try:
            if mount['Source'].index(source) == 0:
                return False
        except:
            pass
    return True

class Service():
    def __init__(self, name, container):
        self.name = name
        self.container = container
