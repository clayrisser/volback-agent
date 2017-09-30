from os import path
from glob import glob
import yaml
from pydash import _

def get_handlers():
    handlers = {}
    for handler_path in glob(path.abspath(path.join(path.dirname(path.realpath(__file__)), '../', 'handlers', '*.yml'))):
        with open(handler_path, 'r') as f:
            data = yaml.load(f)
            for key in data:
                handlers[key] = data[key]
    return handlers
