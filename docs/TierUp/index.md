# TierUp User Guide

TierUp flags Tier 3 variants in GeL interpretation requests that would update classification if reanalysed today. TierUp checks PanelApp for the confidence level of the Tier 3 variant's gene in the current panel version.

## Quick-Start

Install tierup (current development version) in an environment with python >=3.6:
```
git clone https://github.com/NHS-NGS/JellyPy.git -b 0.1.0-tierup.1
pip install JellyPy/tierup
# Run TierUp on interpretation request 1234-1
tierup -irid 1234 --irversion 1 --config configuration.ini
```

### Configuration.ini
A tierup config file with GeL credentials is required:
```
[pyCIPAPI]
username = your_username
password = your_password
```

## Output files

* interpretation.summary.tab - A tab-delimited summary file listing Tiered-Up variants
* interpretation.tierup.csv - A csv file containing the full tierup output