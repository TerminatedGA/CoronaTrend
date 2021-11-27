import argparse
from collections import Counter
import pandas as pd
import itertools
from natsort import natsorted, ns
from tqdm import tqdm
import multiprocess
from multiprocess import Pool
from pathlib import Path
import datetime as dt
from datetime import datetime

parser = argparse.ArgumentParser(description='Generates mutation table sorted by month, along with amino acid mutations and genes involved')
parser.add_argument('--mintotal',  metavar = 'Value', required=True, help="Minimum total number of sequences per time period")
args = vars(parser.parse_args())

inputtotal = args['mintotal']
lineagelimit = 20
minall = 0
maxinit = 100
minchange = -100

mutationdf = pd.read_feather('GISAID-Dataframes/part1temp.feather')
mutationdf.set_index('index')
lineagesorted = pd.read_pickle('GISAID-Dataframes/metadata.pickle', compression = "gzip")[0]

print('Minimum total number of sequences per period to be parsed: {}'.format(inputtotal))
print("Lineages to be parsed: " + ", ".join(lineagesorted))

for index, lineage in zip(range(len(lineagesorted)), lineagesorted):
    print('Now parsing: ' + lineage)
    
    Path("GISAID-Dataframes/{}".format(lineage)).mkdir(parents=True, exist_ok=True)
    Path("GISAID-Dataframes/{}/{}".format(lineage, inputtotal)).mkdir(parents=True, exist_ok=True)
    
    if lineage == 'All':
        lineagedf = mutationdf
    else:
        lineagedf = mutationdf.loc[mutationdf['Lineage'] == lineage]
    countrydfs = lineagedf.groupby(["Country"])
    def gen(df, lineage, minall, minchange, maxinit):  
        tmp = df.groupby(["Week"])

        periodlist = pd.to_datetime(list((df['Week'].unique()))).sort_values().strftime('%Y-%m-%d')
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
        	if totallist[totals] >= float(inputtotal):
	            mutationtablebytimefiltered = mutationtablebytimefiltered.join(mutationtablebytimeraw.iloc[:,totals])
	            totallist1.append(totallist[totals])
	            periodlist1.append(periodlist[totals])
	            
        if len(mutationtablebytimefiltered.loc[aamutationunique[0]]) == 0:
            return 'Error', 'Error'

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

    print("Stage 2 of 3: Generating global dataframe... (Minimum total number of sequences per period: {})".format(inputtotal))

    pxdf1, pxdf2 = gen(lineagedf, lineage, minall, minchange, maxinit)

    #Stores dataframes in .feather format with Zstandard compression for fast decompression and small file size.
    if type(pxdf1) is str:
        print("Null Error: All (Minimum total number of sequences per period: {})".format(inputtotal))
    else:
        pxdf1.to_feather('GISAID-Dataframes/{}/{}/{}_All_1_Mintotal{}.feather'.format(lineage, inputtotal, lineage, inputtotal), compression="zstd", compression_level=19)
        pxdf2.to_feather('GISAID-Dataframes/{}/{}/{}_All_2_Mintotal{}.feather'.format(lineage, inputtotal, lineage, inputtotal), compression="zstd", compression_level=19)

    print("Done\n\nStage 3 of 3: Generating regional dataframes... (Minimum total number of sequences per period: {})".format(inputtotal))
    iterations = 0
    countrylistunique = []                              
                                     
    for countryname, countrydf in countrydfs:
        iterations +=1
                                     
        pxdf1, pxdf2 = gen(countrydf, lineage, minall, minchange, maxinit)
        
        if type(pxdf1) is str:
            print("Null Error: {}/{} ({}) (Minimum total number of sequences per period: {})".format(str(iterations), str(len(countrydfs)), countryname, inputtotal))
            continue

        #Stores dataframes in .feather format with Zstandard compression for fast decompression and small file size.
        pxdf1.to_feather('GISAID-Dataframes/{}/{}/{}_{}_1_Mintotal{}.feather'.format(lineage, inputtotal, lineage, countryname.replace(" ", "_"), inputtotal), compression="zstd", compression_level=19)
        pxdf2.to_feather('GISAID-Dataframes/{}/{}/{}_{}_2_Mintotal{}.feather'.format(lineage, inputtotal, lineage, countryname.replace(" ", "_"), inputtotal), compression="zstd", compression_level=19)
        
        countrylistunique.append(countryname)
        
        print("Done: {}/{} ({}) (Minimum total number of sequences per period: {})".format(str(iterations), str(len(countrydfs)), countryname, inputtotal))

    metadata=pd.Series([countrylistunique])

    metadata.index = ["Countries"]

    metadata.to_pickle('GISAID-Dataframes/{}/{}/{}_metadata_Mintotal{}.pickle'.format(lineage, inputtotal, lineage, inputtotal), compression="gzip")
    
print("\nWork completed successfully (Minimum total number of sequences per period: {})".format(inputtotal))