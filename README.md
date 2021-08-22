[<img src="assets/images/CoronaTrend Logo.png" width="175" height="175">](https://coronatrend.live)

# CoronaTrend

CoronaTrend visualizes data from dataframes generated using GISAID sequences to show up-to-date mutation informtion in different lineages

The website is live at [coronatrend.live](https://coronatrend.live)

Dataframes are generated using _dataframegen.py_.


NOTE 1: 
Sequences where a position has an ambiguous base (e.g. N) are treated as no mutations.

NOTE 2:
Weeks with a total sequence count less than 10 are removed to maintain accuracy of the mutation prevalence.

Known bugs:
1. Setting 'Increase in Prevalence' to a negative value may cause the graph to fail to load.
2. Showing all data from all sequences takes a long time to load.
3. The 'Minimum Increase in Prevalence' parameter only takes account of cases with all dates included.
   Dates filtered with the 'Minimum total number of sequences per time period' are not taken into account.
   
Acknowledgements:
The author thanks Jonathan Daniel Ip for his Python script for translating nucleotide mutations into amino acid mutations.
   
Author: Chan Tze To\
Email: tzetochan@connect.hku.hk


