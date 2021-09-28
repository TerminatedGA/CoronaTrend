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

lineagelimit = 20
minall = 0
maxinit = 100
minchange = -100

genereplacements = [('NSP','nsp'), ("NS", "orf")]

def datetimeable(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except:
        return False
    
def uscdclineage(url):
    r = requests.get(url)

    soup = BeautifulSoup(r.content, "lxml")
    li = soup.find_all("li")

    voilineagelist = []
    voclineagelist = []

    for block in li:
        if block.findPreviousSibling("li") is not None:
            for block2 in block.findPreviousSibling("li"):
                if block2.findPreviousSibling("a", href=re.compile("#anchor_1632150752495")) is not None:
                    for block3 in block2:
                        match = re.search(r'\((.+)\)', str(block3))
                        if match:
                            voilineagelist.append(re.split(', | and ', match.group(0).strip('()')))
                if block2.findPreviousSibling("a", href=re.compile("https://www.cdc.gov/coronavirus/2019-ncov/variants/variant-info.html")) is not None:
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
with open("provision.json", 'r') as provision:
    def loop1(jsonline):
        line = json.loads(jsonline)
        if line['covv_host'] == 'Human' and line['is_high_coverage'] is True and line['is_complete'] is True and line['n_content'] <= 0.05 and datetimeable(line['covv_collection_date']):
            weeklistmid = datetime.strptime(line['covv_collection_date'], '%Y-%m-%d')
            weeklistmid = weeklistmid - dt.timedelta(days=weeklistmid.weekday() % 7)
            sequencelistmid = line['covv_accession_id']
            lineagelistmid = line['covv_lineage']
            locations = [location.strip() for location in line['covv_location'].split('/')]
            countrylistmid = locations[1]
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
for lineage in lineagelist2:
    if lineage in lineagesorted:
        lineagelist1.append(lineage)
        
lineagesorted = natsorted(list(set(lineagesorted[:20] + lineagelist1)))
lineagesorted.insert(0, "All")

print('Generating week from date')

mutationdata = {"Week": pd.Series(weeklist, dtype='category'), 
                "Country": pd.Series(countrylist, dtype='category'), 
                "Lineage": pd.Series(lineagelist, dtype='category'), 
                "AA Mutations": aalabellistlist}
mutationdf = pd.DataFrame(mutationdata)
mutationdf.index = sequencelist

print("Lineages to be parsed: " + ", ".join(lineagesorted))

for index, lineage in zip(range(len(lineagesorted)), lineagesorted):
    print('Now parsing: ' + lineage)
    
    Path("GISAID-Dataframes/{}".format(lineage)).mkdir(parents=True, exist_ok=True)
    
    if lineage == 'All':
        lineagedf = mutationdf
    else:
        lineagedf = mutationdf.loc[mutationdf['Lineage'] == lineage]
    countrydfs = lineagedf.groupby(["Country"])
    def gen(df, lineage, minall, minchange, maxinit):  
        tmp = df.groupby(["Week"])

        periodlist = pd.to_datetime(list((df['Week'].unique()))).sort_values().strftime('%Y-%m-%d')
        sequencetotalbyperiod = []
        percentagelistlist = []
        totallist = []

        aamutationunique = natsorted(list(set(itertools.chain.from_iterable(df["AA Mutations"]))), alg=ns.FLOAT)
        if aamutationunique == []:
            return 'Error', 'Error'

        for period in range(len(periodlist)):
            periodsequences = tmp.get_group(periodlist[period])
            percentagelist=[]
            groupaamutationtotal = list(itertools.chain.from_iterable(list(periodsequences['AA Mutations'])))
            groupaamutationcount = Counter(groupaamutationtotal)
            groupaamutationcounts = {}
            for aamutation in aamutationunique:
                if aamutation not in groupaamutationcount.keys():
                    groupaamutationcount[aamutation] = 0
                groupaamutationcounts[aamutation] = groupaamutationcount.get(aamutation)
            percentagelist = [x * 100/ len(periodsequences) for x in groupaamutationcounts.values()]
            #percentagelist = [round(num, 3) for num in percentagelist] # for rounding to 3 sig. fig.
            percentagelistlist.append(percentagelist)
            totallist.append(len(periodsequences))

        mutationtablebytimeraw = pd.DataFrame(percentagelistlist, index = periodlist, columns = aamutationunique).transpose()

        mutationtablebytimefiltered = pd.DataFrame(index = aamutationunique)
        totallist1 = []
        periodlist1 = []

        for totals in range(len(totallist)):
            mutationtablebytimefiltered = mutationtablebytimefiltered.join(mutationtablebytimeraw.iloc[:,totals])
            totallist1.append(totallist[totals])
            periodlist1.append(periodlist[totals])

        def loop2(aamutation2):
            if max(set(mutationtablebytimefiltered.loc[aamutation2])) >= minall and mutationtablebytimefiltered.loc[aamutation2][-1] - mutationtablebytimefiltered.loc[aamutation2][0] >= minchange and mutationtablebytimefiltered.loc[aamutation2][0] <= maxinit:
                initlistmid = mutationtablebytimefiltered.loc[aamutation2][0]
                percentagelistlistmid = list(mutationtablebytimefiltered.loc[aamutation2])
                maxprevalencelistmid = max(set(mutationtablebytimefiltered.loc[aamutation2]))
                maxprevalencechangelistmid = mutationtablebytimefiltered.loc[aamutation2][-1] - mutationtablebytimefiltered.loc[aamutation2][0]
                maxprevalencechangealllistmid = max(set(mutationtablebytimefiltered.loc[aamutation2])) - min(set(mutationtablebytimefiltered.loc[aamutation2]))
                return [aamutation2, initlistmid, percentagelistlistmid, maxprevalencechangealllistmid, maxprevalencelistmid, maxprevalencechangelistmid]

        with Pool(multiprocess.cpu_count()-1) as p:
            aamutationlist, initlist, percentagelistlist, maxprevalencechangealllist, maxprevalencelist, maxprevalencechangelist = [d for d in zip(*[x for x in list(p.imap(loop2, tqdm(aamutationunique, position=0, leave=True), chunksize = 50)) if x is not None])]
        #Create dataframes for Dash app
        pxdf1 = pd.DataFrame()
        pxdf1['Maximum prevalence (%)'] = [float(a) for a in maxprevalencelist]
        pxdf1['Change in prevalence (Fin - Start)(%)'] = [float(a) for a in maxprevalencechangelist]
        pxdf1['Change in prevalence (All)(%)'] = [float(a) for a in maxprevalencechangealllist]
        pxdf1['Initial prevalence'] = [float(a) for a in initlist]
        pxdf1['Percentage by period'] = [[float(b) for b in a] for a in percentagelistlist]
        pxdf1['Gene'] = [aamut.split(':')[0] for aamut in aamutationlist]
        pxdf1['AA Label'] = aamutationlist

        pxdf2 = pd.DataFrame()
        pxdf2['Totals'] = totallist1
        pxdf2['Periods'] = periodlist1
        pxdf2['Label'] = 'Total Number of Sequences'

        return pxdf1, pxdf2

    print("Stage 2 of 3: Generating global dataframe...")

    pxdf1, pxdf2 = gen(lineagedf, lineage, minall, minchange, maxinit)

    #Stores dataframes in .feather format with Zstandard compression for fast decompression and small file size.
    if type(pxdf1) is str:
        print("Null Error: All")
    else:
        pxdf1.to_feather('GISAID-Dataframes/{}/{}_All_1.feather'.format(lineage, lineage), compression="zstd", compression_level=19)
        pxdf2.to_feather('GISAID-Dataframes/{}/{}_All_2.feather'.format(lineage, lineage), compression="zstd", compression_level=19)

    print("Done\n\nStage 3 of 3: Generating regional dataframes...")
    iterations = 0
    countrylistunique = []                              
                                     
    for countryname, countrydf in countrydfs:
        iterations +=1
                                     
        pxdf1, pxdf2 = gen(countrydf, lineage, minall, minchange, maxinit)
        
        if type(pxdf1) is str:
            print("Null Error: {}/{} ({})".format(str(iterations), str(len(countrydfs)), countryname))
            continue

        #Stores dataframes in .feather format with Zstandard compression for fast decompression and small file size.
        pxdf1.to_feather('GISAID-Dataframes/{}/{}_{}_1.feather'.format(lineage, lineage, countryname.replace(" ", "_")), compression="zstd", compression_level=19)
        pxdf2.to_feather('GISAID-Dataframes/{}/{}_{}_2.feather'.format(lineage, lineage, countryname.replace(" ", "_")), compression="zstd", compression_level=19)
        
        countrylistunique.append(countryname)
        
        print("Done: {}/{} ({})".format(str(iterations), str(len(countrydfs)), countryname))

    metadata=pd.Series([countrylistunique])

    metadata.index = ["Countries"]

    metadata.to_pickle('GISAID-Dataframes/{}/{}_metadata.pickle'.format(lineage, lineage), compression="gzip")

metadata = pd.Series([lineagesorted[:lineagelimit+1]])
metadata.to_pickle('GISAID-Dataframes/metadata.pickle', compression="gzip")
    
print("\nWork completed successfully")