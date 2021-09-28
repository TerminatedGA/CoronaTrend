import os

try:
    os.remove('provision.json')
    print('Deleted "provision.json"')
except OSError:
    print('Error: Unable to delete "provison.json": "provison.json" does not exist!')
