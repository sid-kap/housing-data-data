#! /usr/bin/env python3.8
from subprocess import Popen
from pathlib import Path
import shutil

REGIONS = [
    ('so', 'South Region'),
    ('ne', 'Northeast Region'),
    ('we', 'West Region'),
    ('mw', 'Midwest Region'),
]
PREFIX = 'https://www2.census.gov/econ/bps/'
DATA_ROOT = Path('./data')

def get_place_path(year, region_tuple):
    return f'Place/{region_tuple[1]}/{region_tuple[0]}{year:04d}a.txt'

def get_county_path(year):
    return f'County/co{year:04d}a.txt'

def get_metro_path(year):
    return f'Metro/ma{year:04d}a.txt'

def get_state_path(year):
    return f'State/st{year:04d}a.txt'

def main():
    shutil.rmtree(DATA_ROOT)

    paths = []
    for year in range(1980, 2021):
        for region_tuple in REGIONS:
            paths.append(get_place_path(year, region_tuple))
        paths.append(get_county_path(year))
        paths.append(get_metro_path(year))
        paths.append(get_state_path(year))

    for path in paths:
        output_path = Path(DATA_ROOT, path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        Popen(['wget', PREFIX + path, '-P', str(output_path.parent)])

if __name__ == '__main__':
    main()
