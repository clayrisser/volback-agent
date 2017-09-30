# def backup_mount(mount_path, backup_path, borg, data_type, container):
#     image = container['Config']['Image'].encode('utf8')
#     timestamp = time.time()
#     backup_name = encode_backup_name(timestamp, mount['Destination'], image)
#     if not path.isdir(mount_path):
#         raise MountPathNotFound(mount_path)
#     with open(path.join(mount_path, self.config_filename), 'w') as f:
#         yaml.dump({
#             'source': mount['Source'].encode('utf8'),
#             'destination': mount['Destination'].encode('utf8'),
#             'timestamp': timestamp,
#             'data_type': data_type,
#             'image': image
#         }, f, default_flow_style=False)
#         borg.create(backup_name, mount_path)
#             os.remove(path.join(mount_path, self.config_filename))

#     pass

# def restore_mount():
#     pass
