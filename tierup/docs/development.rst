Development
===========

Testing
-------

Install developer tools:
`pip install -r tierup/dev_requirements.txt` to install developer tools.

Tests are run with pytest, for which a `tierup/test/config.ini` must be created:
```
[pyCIPAPI]
username = your_username
password = your_pass
test_irid = 123123
test_irversion = 1
```

The test config resembles the jellypy config with additional arguments:
* `test_irid` - An interpretation request id to use when testing downloads. See `test/test_requests.py`
* `test_irversion` - An interpretation request version to use when testing downloads. See `test/test_requests.py`

Documentation
-------------

Docs are built from the docs/ directory with Sphinx.
The HTML files are uploaded to https://acgs.gitbook.io/bioinformatics/jellypy-docs.
