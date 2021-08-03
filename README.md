
# CoronaTrend

CoronaTrend visualizes data from dataframes generated using GISAID sequences to show up-to-date mutation informtion in different lineages

The website is live at [coronatrend.live](coronatrend.live)

Dataframes are generated using _dataframegen.py_.


NOTE 1: 
Sequences where a position has an ambiguous base (e.g. N) are treated as no mutations.

NOTE 2:
Weeks with a total sequence count less than 10 are removed to maintain accuracy of the mutation prevalence.


