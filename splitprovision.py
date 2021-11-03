#!/usr/bin/env python
import multiprocess
import fileinput
import json


def split(jsonline):
    line = json.loads(jsonline)
    filterlist = ['sequence', 
                  'covv_virus_name', 
                  'covv_type', 
                  'covv_variant', 
                  'gc_content', 
                  'covv_passage', 
                  'covsurver_uniquemutlist', 
                  'covv_clade', 
                  'is_reference', 
                  'pangolin_lineages_version', 
                  'covv_subm_date', 
                  'sequence_length']
    for element in filterlist:
    	line.pop(element)
    print('{}\n'.format(json.dumps(line)), end = '')

p = multiprocess.Pool()
gen = list(p.imap(split, fileinput.input(), chunksize=2000))