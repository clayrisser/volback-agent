from os import path
from bisect import bisect_left
import encode_service
import time

def find_timestamp(restore_time, destination, image, borg):
    timestamp = time.time()
    if restore_time:
        timestamp = time.mktime(dateparser.parse(restore_time).timetuple())
    timestamps = list()
    for backup_name_str in borg.list():
        backup_name = encode_service.decode_backup_name(backup_name_str)
        if backup_name.image == image and backup_name.destination == destination:
            timestamps.append(backup_name.timestamp)
    if len(timestamps) <= 0:
        return None
    return closest_timestamp(timestamps, timestamp)

def closest_timestamp(timestamps, timestamp):
    pos = bisect_left(timestamps, timestamp)
    if pos == 0:
        return timestamps[0]
    if pos == len(timestamps):
        return timestamps[-1]
    before = timestamps[pos - 1]
    after = timestamps[pos]
    if after - timestamp < timestamp - before:
        return after
    return before

def get_unique_path(parent_path):
    unique_path = path.join(parent_path, 'volback-unique-' + encode_service.str_encode(str(time.time())))
    if path.exists(unique_path):
        unique_path = get_unique_path(unique_path)
    return unique_path
