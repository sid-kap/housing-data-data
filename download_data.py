#! /usr/bin/env python3.10
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

LATEST_MONTH = (2022, 6)

# Whether to download the monthly files from December of the latest full year of data available.
# This is needed in Jan-May of each year, because the full year's estimates (imputing the
# small counties that don't get surveyed every month) for the previous year don't come out until
# May.
# Arguably, we could just always download the December estimate for the previous year, even if it's
# not strictly needed. But let's do this for now, can revisit later.
GET_PREVIOUS_YEAR_DECEMBER_MONTHLY_DATA = False
PREVIOUS_YEAR = 2021


def download_to_directory(url: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    Popen(["wget", url, "-P", str(output_dir)])


####################################################
# BPS downloading functions
####################################################


def get_place_path(year_or_year_month, region_tuple, frequency="a"):
    return f"Place/{region_tuple[1]}/{region_tuple[0]}{year_or_year_month:04d}{frequency}.txt"


def get_county_path(year_or_year_month, frequency="a"):
    return f"County/co{year_or_year_month:04d}{frequency}.txt"


def get_metro_path(year_or_year_month, frequency="a"):
    return f"Metro/ma{year_or_year_month:04d}{frequency}.txt"


def get_state_path(year_or_year_month, frequency="a"):
    return f"State/st{year_or_year_month:04d}{frequency}.txt"


def download_bps_data():
    paths = []

    max_annual_year = PREVIOUS_YEAR if GET_PREVIOUS_YEAR_DECEMBER_MONTHLY_DATA else PREVIOUS_YEAR + 1
    for year in range(1980, max_annual_year):
        for region_tuple in REGIONS:
            paths.append(get_place_path(year, region_tuple))
        if year >= 1990:
            paths.append(get_county_path(year))
        paths.append(get_metro_path(year))
        paths.append(get_state_path(year))

    monthly_datasets = [LATEST_MONTH]
    if GET_PREVIOUS_YEAR_DECEMBER_MONTHLY_DATA:
        monthly_datasets.append((PREVIOUS_YEAR, 12))

    for year, month in monthly_datasets:
        # Last two digits of year followed by month number
        latest_year_month = (year % 100) * 100 + month
        for region_tuple in REGIONS:
            paths.append(get_place_path(latest_year_month, region_tuple, frequency="y"))
        paths.append(get_county_path(latest_year_month, frequency="y"))
        paths.append(get_metro_path(latest_year_month, frequency="y"))
        paths.append(get_state_path(latest_year_month, frequency="y"))

    for path in paths:
        output_dir = Path(DATA_ROOT, "bps", path).parent
        download_to_directory(PREFIX + path, output_dir)


####################################################
# Census population downloading functions
####################################################

STATE_POPULATION_PATHS = [
    "https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st8090ts.txt",
    "https://www2.census.gov/programs-surveys/popest/tables/2010-2019/state/totals/nst-est2019-01.xlsx",
    "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/state/totals/nst-est2020-alldata.csv",
    "https://www2.census.gov/programs-surveys/popest/tables/2000-2010/intercensal/state/st-est00int-01.xls",
] + [
    f"https://www2.census.gov/programs-surveys/popest/tables/1990-2000/intercensal/st-co/stch-icen{year}.txt"
    for year in range(1990, 2000)
]

COUNTY_POPULATION_PATHS = (
    [
        "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv",
        "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/co-est2020-alldata.csv",
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
    "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/cities/SUB-EST2020_ALL.csv",
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
