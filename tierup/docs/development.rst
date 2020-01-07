Development
===========

Setup
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


Running Tests
-------------

Run all tests in the directory:
`pytest tierup/test --jpconfig=path_to_your_test_config.ini`

Tests have been separated into files with the following rationale:
* test_requests.py - These tests call the GeL CIPAPI. Users must be on the NHS Health and Social Care Network for these requests to work.
* test_modules.py - Test various objects in the tierup library
* test_tierup.py - Test the application using a local json file

Documentation
-------------

Docs are built from the docs/ directory with Sphinx.
The HTML files are uploaded to https://acgs.gitbook.io/bioinformatics/jellypy-docs.
