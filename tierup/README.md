# jellypy-tierup

TierUp is a jellypy module for reanalysing Tier 3 variants in GEL 100KG cases.

At the time of initial analysis, all Tier 3 variants are found in low-confidence genes in their associated PanelApp panel. TierUp checks for  confidence level increases, reporting variants that meet Tier 1 or 2 criteria today.

## Documentation
https://acgs.gitbook.io/bioinformatics/jellypy-docs

## Installation

pip install ./tierup

## Usage

> tierup -i 12354-1 -c tierup_config.ini

The `tierup_config.ini` file format:
``` tierup_config.ini
[pyCIPAPI]
pyCIPAPI_USERNAME = me
pyCIPAPI_PASSWORD = pass

[tierup]
tierup_STDOUT = TRUE
tierup_IRJOUT = /home/Documents/interpretation_requests
```

**Note**: In the usage example above, access to the NHS N3 network is required for TierUp to download interpretation request data. Pass pre-existing data in GEL v6 json format as follows:
> tierup --json 12354-1.json --config tierup_config.ini


## Contributing
1. Fork it!
1. Create your feature branch: git checkout -b my-new-feature
1. Commit your changes: git commit -am 'Add some feature'
1. Push to the branch: git push origin my-new-feature
1. Submit a pull request :D

## History