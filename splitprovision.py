import fileinput
import json
#with open("provision.fasta", "w+") as fasta:
for jsonline in fileinput.input():
    line = json.loads(jsonline)
    #fasta.write('>{}\n{}\n'.format(line['covv_accession_id'], line['sequence'].replace('\n', '')))
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