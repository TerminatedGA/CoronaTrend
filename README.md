[<img src="assets/images/CoronaTrend Logo.png" width="175" height="175">](https://coronatrend.live)

# CoronaTrend #

CoronaTrend visualizes data from dataframes generated using GISAID sequences to show up-to-date mutation informtion in different lineages

The website is live at [coronatrend.live](https://coronatrend.live)

Dataframes are generated using _dataframegen.py_ found in [github.com/TerminatedGA/GISAID-Dataframes](https://github.com/TerminatedGA/GISAID-Dataframes)\.

## Notes ##

1. Sequences where a position has an ambiguous base (e.g. N) are treated as no mutations.

## Known bugs ##

1. Setting 'Increase in Prevalence' to a negative value may cause the graph to fail to load.
2. Showing all data from all sequences takes a long time to load.
3. The 'Minimum Increase in Prevalence' parameter only takes account of cases with all dates included.
   Dates filtered with the 'Minimum total number of sequences per time period' are not taken into account.
   
## Acknowledgements ##

CoronaTrend is a project coordinated by Chan Tze To under the supervision of Dr. Kelvin To, along with assistance from Mr. Jonathan Ip.

We gratefully acknowledge all data contributors, i.e. the Authors and their Originating laboratories responsible for obtaining the specimens, and their Submitting laboratories for generating the genetic sequence and metadata and sharing via the GISAID Initiative (1), on which this research is based.

1) Elbe, S., and Buckland-Merrett, G. (2017) Data, disease and diplomacy: GISAID’s innovative contribution to global health. Global Challenges, 1:33-46. DOI: [10.1002/gch2.1018](https://dx.doi.org/10.1002/gch2.1018) PMCID: [31565258](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6607375/)

## Contact ##

Author: Chan Tze To\
Email: tzetochan@connect.hku.hk


