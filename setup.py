import os
from setuptools import setup, find_packages


setup(
    name="cds-test",
    version="0.0.0",
    include_package_data=True,
    packages=find_packages(),
    description="cds-test-module",
    author="Anil Bodepudi",
    install_requires=[
'Flask',
'pandas',
'zipfile36',
'numpy==1.17.4',
'folium',
'plotly',
'xarray',
'cdsapi',

    ],
)
