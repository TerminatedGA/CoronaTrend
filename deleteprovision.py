import os

try:
    os.remove('provision.json.xz')
    print('Deleted "provision.json.xz"')
except OSError:
    print('Error: Unable to delete "provison.json.xz": "provison.json.xz" does not exist!')
