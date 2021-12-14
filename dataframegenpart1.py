#!/usr/bin/env python

import json
from collections import Counter
import re
import pandas as pd
import itertools
from natsort import natsorted, ns
from tqdm import tqdm
import multiprocess
from multiprocess import Pool
from pathlib import Path
import datetime as dt
from datetime import datetime
from bs4 import BeautifulSoup
import pycurl_requests as requests
import lzma

Path("GISAID-Dataframes").mkdir(parents=True, exist_ok=True)

genereplacements = [('NSP','nsp'), ("NS", "orf")]

def datetimeable(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except:
        return False
        
compile1 = re.compile("#anchor_1632150752495")
compile2 = re.compile("https://www.cdc.gov/coronavirus/2019-ncov/variants/variant-info.html")
    
def uscdclineage(url):
    r = requests.get(url)

    soup = BeautifulSoup(r.content, "lxml")
    li = soup.find_all("li")

    voilineagelist = []
    voclineagelist = []

    for block in li:
        if block.findPreviousSibling("li") is not None:
            for block2 in block.findPreviousSibling("li"):
                if block2.findPreviousSibling("a", href=compile1) is not None:
                    for block3 in block2:
                        match = re.search(r'\((.+)\)', str(block3))
                        if match:
                            voilineagelist.append(re.split(', | and ', match.group(0).strip('()')))
                if block2.findPreviousSibling("a", href=compile2) is not None:
                    for block3 in block2:
                        match = re.search(r'\((.+)\)', str(block3))
                        if match:
                            voclineagelist.append(re.split(', | and ', match.group(0).strip('()')))

    def lineagefilter(lineagelist):
        lineagelist = list(set(list(itertools.chain.from_iterable(lineagelist))))
        lineagelist = [x.split()[0] for x in lineagelist if len(x)!=1]
        return lineagelist

    voclineagelist = lineagefilter(voclineagelist)

    voilineagelist = lineagefilter(voilineagelist)

    lineagelist2 = list(set(voclineagelist + voilineagelist))
    
    return lineagelist2

print("Stage 1 of 3: Generating stats for each sequence")
with lzma.open("provision.json.xz", 'r') as provision:
    def loop1(jsonline):
        line = json.loads(jsonline)
        if line['covv_host'] == 'Human' and line['is_high_coverage'] is True and line['is_complete'] is True and line['n_content'] <= 0.05 and datetimeable(line['covv_collection_date']):
            weeklistmid = datetime.strptime(line['covv_collection_date'], '%Y-%m-%d')
            weeklistmid = weeklistmid - dt.timedelta(days=weeklistmid.weekday() % 7)
            sequencelistmid = line['covv_accession_id']
            lineagelistmid = line['covv_lineage']
            locations = [location.strip() for location in line['covv_location'].split('/')]
            countrylistmid = locations[1].replace("Hong Kong", "Hong Kong SAR")
            aamutationsplit = re.split(',|_', line['covsurver_prot_mutations'].translate({ord(ch):' ' for ch in '()'}).strip())
            aalabellistlistmid = []
            for gene, aamut in zip(aamutationsplit[::2], aamutationsplit[1::2]):
                for old, new in genereplacements:
                    gene = re.sub(old, new, gene)
                aalabellistlistmid.append(gene + ": " + aamut)
                
            return [weeklistmid, sequencelistmid, lineagelistmid, countrylistmid, aalabellistlistmid]
    
    with Pool(multiprocess.cpu_count()-1) as p:
        weeklist, sequencelist, lineagelist, countrylist, aalabellistlist = [d for d in zip(*[x for x in list(p.imap(loop1, tqdm(provision, position=0, leave=True), chunksize = 2000)) if x is not None])]

print('Stage 1 completed successfully\n\nCounting lineages')

lineagedict = dict(Counter(lineagelist))
lineagedictsorted = dict(sorted(lineagedict.items(), key=lambda kv: kv[1], reverse=True))
lineagesorted = list(lineagedictsorted.keys())
lineagelist1 = []
url = 'https://www.cdc.gov/coronavirus/2019-ncov/variants/variant-info.html'
lineagelist2 = uscdclineage(url)
lineagelist2.extend(['B.1.36.27', 'B.1.36', 'B.1.214.2', 'B.1.466.2', 'B.1.619', 'B.1.620', 'B.1.1.63', 'B.1.1.318', 'B.1.1.519', 'B.1.1.523', 'B.1.1.529', 'C.1.2', 'C.36.3', 'C.37', 'R.1'])
for lineage in lineagelist2:
    if lineage in lineagesorted:
        lineagelist1.append(lineage)
        
lineagesorted = natsorted(list(set(lineagesorted[:20] + lineagelist1)))
lineagesorted.insert(0, "All")

lineagelist1 = None
lineagelist2 = None

print('Generating week from date')

mutationdata = {"Week": pd.Series(weeklist, dtype='category'), 
                "Country": pd.Series(countrylist, dtype='category'), 
                "Lineage": pd.Series(lineagelist, dtype='category'), 
                "AA Mutations": aalabellistlist}

mutationdf = pd.DataFrame(mutationdata)
mutationdf['index'] = sequencelist

mutationdf.to_feather('GISAID-Dataframes/part1temp.feather', compression="zstd", compression_level=19)

weeklist = None
sequencelist = None
lineagelist = None
countrylist = None
aalabellistlist = None

metadata = pd.Series([lineagesorted])
metadata.to_pickle('GISAID-Dataframes/metadata.pickle', compression="gzip")