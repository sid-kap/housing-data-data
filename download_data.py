#! /usr/bin/env python3.8
import shutil
from pathlib import Path
from subprocess import Popen

REGIONS = [
    ("so", "South Region"),
    ("ne", "Northeast Region"),
    ("we", "West Region"),
    ("mw", "Midwest Region"),
]
PREFIX = "https://www2.census.gov/econ/bps/"
DATA_ROOT = Path("./data")


def download_to_directory(url: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    Popen(["wget", url, "-P", str(output_dir)])


####################################################
# BPS downloading functions
####################################################


def get_place_path(year, region_tuple):
    return f"Place/{region_tuple[1]}/{region_tuple[0]}{year:04d}a.txt"


def get_county_path(year):
    return f"County/co{year:04d}a.txt"


def get_metro_path(year):
    return f"Metro/ma{year:04d}a.txt"


def get_state_path(year):
    return f"State/st{year:04d}a.txt"


def download_bps_data():
    paths = []
    for year in range(1980, 2021):
        for region_tuple in REGIONS:
            paths.append(get_place_path(year, region_tuple))
        paths.append(get_county_path(year))
        paths.append(get_metro_path(year))
        paths.append(get_state_path(year))

    for path in paths:
        output_dir = Path(DATA_ROOT, "bps", path).parent
        download_to_directory(PREFIX + path, output_dir)


####################################################
# Census population downloading functions
####################################################

STATE_POPULATION_PATHS = [
    "https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st8090ts.txt",
    "https://www2.census.gov/programs-surveys/popest/tables/2010-2019/state/totals/nst-est2019-01.xlsx",
    "https://www2.census.gov/programs-surveys/popest/tables/2000-2010/intercensal/state/st-est00int-01.xls",
] + [
    f"https://www2.census.gov/programs-surveys/popest/tables/1990-2000/intercensal/st-co/stch-icen{year}.txt"
    for year in range(1990, 2000)
]

COUNTY_POPULATION_PATHS = (
    [
        "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv",
        "https://www2.census.gov/programs-surveys/popest/geographies/2019/all-geocodes-v2019.xlsx",
        "https://www2.census.gov/programs-surveys/popest/tables/1990-2000/counties/totals/99c8_00.txt",
    ]
    + [
        f"https://www2.census.gov/programs-surveys/popest/tables/2000-2010/intercensal/county/co-est00int-01-{state_fips:02d}.csv"
        # Not sure why the state fips are this weird series rather than just 1 through 50.
        for state_fips in range(1, 57)
        if state_fips not in {3, 7, 11, 14, 43, 52}
    ]
    + [
        f"https://www2.census.gov/programs-surveys/popest/tables/1980-1990/counties/asrh/pe-02-{year}.xls"
        for year in range(1980, 1990)
    ]
)


PLACE_POPULATION_PATHS = [
    "https://www2.census.gov/geo/tiger/PREVGENZ/pl/us_places.txt",
    "https://www2.census.gov/programs-surveys/popest/tables/1990-2000/2000-subcounties-evaluation-estimates/sc2000f_us.txt",
    "https://www2.census.gov/programs-surveys/popest/datasets/2000-2010/intercensal/cities/sub-est00int.csv",
    "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/cities/totals/sub-est2019_all.csv",
]

POPULATION_ROOT = Path(DATA_ROOT, "population")
STATE_POPULATION_ROOT = Path(POPULATION_ROOT, "state")
COUNTY_POPULATION_ROOT = Path(POPULATION_ROOT, "county")
PLACE_POPULATION_ROOT = Path(POPULATION_ROOT, "place")


def download_population_data():
    for path in STATE_POPULATION_PATHS:
        download_to_directory(path, STATE_POPULATION_ROOT)

    for path in COUNTY_POPULATION_PATHS:
        download_to_directory(path, COUNTY_POPULATION_ROOT)

    for path in PLACE_POPULATION_PATHS:
        download_to_directory(path, PLACE_POPULATION_ROOT)


####################################################
# Main
####################################################


def main():
    DATA_ROOT.mkdir(exist_ok=True)
    shutil.rmtree(DATA_ROOT)

    download_bps_data()
    download_population_data()


if __name__ == "__main__":
    main()
