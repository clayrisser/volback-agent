import base64
import re

class BackupName():
    def __init__(self, timestamp, destination, image):
        self.timestamp = timestamp
        self.destination = destination
        self.image = image

def decode_backup_name(backup_name_str):
    timestamp = None
    destination = None
    image = None
    backup_name_str = str_decode(backup_name_str)
    matches = re.findall(r'^[^\|]+', backup_name_str)
    if len(matches) > 0:
        timestamp = float(matches[0])
    matches = re.findall(r'(?<=\|).+(?=\|)', backup_name_str)
    if len(matches) > 0:
        destination = str_decode(matches[0])
    matches = re.findall(r'[^\|]+$', backup_name_str)
    if len(matches) > 0:
        image = str_decode(matches[0])
    return BackupName(
        timestamp=timestamp,
        destination=destination,
        image=image
    )

def encode_backup_name(poly, destination=None, image=None):
    backup_name = None
    timestamp = None
    if not image and not destination:
        backup_name = poly
        timestamp = backup_name.timestamp
        destination = backup_name.destination
        image = backup_name.image
    else:
        timestamp = poly
    return str_encode(str(timestamp) + '|' + str_encode(destination) + '|' + str_encode(image))

def str_encode(string):
    return base64.b64encode(string).replace('=', '')

def str_decode(string):
    return base64.b64decode(string + ('=' * (-len(string) % 4)))
