[<img src="assets/images/CoronaTrend Logo.png" width="175" height="175">](https://coronatrend.live)

# CoronaTrend #

CoronaTrend visualizes data from dataframes generated using GISAID sequences to show up-to-date mutation informtion in different lineages

The website is live at [coronatrend.live](https://coronatrend.live)

Dataframes are generated using _provision.sh_.

## Sequence filtering criteria ##
All SARS-CoV-2 sequences used in CoronaTrend meets the following criteria:\

Host: Human\
Sequencing Coverage: High\
Sequence is Complete: True\
N Content: ≤5%

## Notes ##
1. CoronaTrend is only able to show point mutations such as substitution mutations, insertion mutations, deletion mutations and nonsense mutations.
2. Sequences where a position has an ambiguous base (e.g. N) are treated as no mutations.

## Known bugs ##

1. Setting 'Increase in Prevalence' to a negative value may cause the graph to fail to load.
2. Showing all data from all sequences takes a long time to load.
   
## Acknowledgements ##

CoronaTrend is a project coordinated by Chan Tze To under the supervision of Dr. Kelvin To, along with assistance from Mr. Jonathan Ip.

We gratefully acknowledge all data contributors, i.e. the Authors and their Originating laboratories responsible for obtaining the specimens, and their Submitting laboratories for generating the genetic sequence and metadata and sharing via the GISAID Initiative (1), on which this research is based.

1) Elbe, S., and Buckland-Merrett, G. (2017) Data, disease and diplomacy: GISAID’s innovative contribution to global health. Global Challenges, 1:33-46. DOI: [10.1002/gch2.1018](https://dx.doi.org/10.1002/gch2.1018) PMCID: [31565258](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6607375/)

## Contact ##
All enquires regarding CoronaTrend can be sent to contact@coronatrend.live.

Author: Chan Tze To\
Email: tzetochan@connect.hku.hk 


