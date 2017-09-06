import docker
import pydash as _

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def get_container(container_id):
    return client.containers.get(container_id).attrs

def get_containers(container_ids=None):
    containers = list()
    if container_ids:
        for container_id in container_ids:
            containers.append(get_container(container_id))
    else:
        for container in client.containers.list():
            containers.append(container.attrs)
    return containers

def get_mounts(container_ids=None):
    mounts = list()
    for container in get_containers(container_ids):
        mounts = _.flatten([mounts, container['Mounts']])
    return mounts
