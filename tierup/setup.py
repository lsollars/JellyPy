from setuptools import find_packages, setup

setup(
    name='jellypy_tierup',
    version='0.1.0',
    author="NHS Bioinformatics Group",
    author_email="nana.mensah1@nhs.net",
    description='Python library for checking GeL Tier 3 variants with Green PanelApp genes',
    license="TBC",
    url='https://github.com/NHS-NGS/JellyPy',
    packages=find_packages(),
    package_data={'':['data/*.schema']},
    install_requires=[
        'click==7.0',
        'jsonschema==3.2.0',
    ],
    dependency_links=[
        'https://test.pypi.org/project/jellypy-pyCIPAPI/0.1.0/'
    ],
    entry_points = {
        'console_scripts': 'tierup=jellypy.tierup.interface:cli'
    }
)
