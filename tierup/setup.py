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
    install_requires=[
        'jellypy-pyCIPAPI'
    ],
    dependency_links = ['https://github.com/NHS-NGS/JellyPy/tree/0.1.0-dev/pyCIPAPI#egg=jellypy-pyCIPAPI-0.1.0']
)
