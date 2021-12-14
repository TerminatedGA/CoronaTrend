#!/usr/bin/env python

import os

try:
    os.remove('provision.json.xz')
    print('Deleted "provision.json.xz"')

except OSError:
    print('Error: Unable to delete "provison.json.xz": "provison.json.xz" does not exist!')
    
try:
    os.remove('GISAID-Dataframes/part1temp.feather')
    print('Deleted "GISAID-Dataframes/part1temp.feather"')

except OSError:
    print('Error: Unable to delete "GISAID-Dataframes/part1temp.feather": "GISAID-Dataframes/part1temp.feather" does not exist!')

