#! /usr/bin/env python3.10
import shutil
from pathlib import Path
from subprocess import Popen, run
from tempfile import TemporaryDirectory

DATA_ROOT = Path("./data")
DOWNLOAD_LOG_PATH = Path("download.log")

REGIONS = [
    ("so", "South Region"),
    ("ne", "Northeast Region"),
    ("we", "West Region"),
    ("mw", "Midwest Region"),
]
PREFIX = "https://www2.census.gov/econ/bps/"

LATEST_MONTH = (2022, 9)

# Whether to download the monthly files from December of the latest full year of data available.
# This is needed in Jan-May of each year, because the full year's estimates (imputing the
# small counties that don't get surveyed every month) for the previous year don't come out until
# May.
# Arguably, we could just always download the December estimate for the previous year, even if it's
# not strictly needed. But let's do this for now, can revisit later.
GET_PREVIOUS_YEAR_DECEMBER_MONTHLY_DATA = False
PREVIOUS_YEAR = 2021


def download_to_directory(url: str, output_dir: Path) -> None:
    # Downloads async (in parallel)
    output_dir.mkdir(parents=True, exist_ok=True)
    Popen(["wget", url, "-P", str(output_dir), "-a", DOWNLOAD_LOG_PATH])


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

    max_annual_year = (
        PREVIOUS_YEAR if GET_PREVIOUS_YEAR_DECEMBER_MONTHLY_DATA else PREVIOUS_YEAR + 1
    )
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
# Canada crosswalk downloading functions
####################################################

CANADA_CROSSWALK_PATH = Path(DATA_ROOT, "canada-crosswalk")


CANADA_CROSSWALK_FILES = [
    "CSD.csv",
    "CD.csv",
    "PR.csv",
    "CMA_CA.csv",
]


def download_canada_crosswalk_data():
    with TemporaryDirectory() as temp_dir:
        print("Downloading Canada crosswalk zip")
        run(
            [
                "wget",
                "https://www12.statcan.gc.ca/census-recensement/2021/geo/aip-pia/geosuite/files-fichiers/2021_92-150-X_eng.zip",
                "-P",
                temp_dir,
                "-a",
                DOWNLOAD_LOG_PATH,
            ],
            check=True,
        )
        run(["ls", temp_dir])
        print("Unzipping")
        run(["7z", "x", "2021_92-150-X_eng.zip"], check=True, cwd=temp_dir)
        run(["mv", temp_dir + "/2021_92-150-X_eng", CANADA_CROSSWALK_PATH], check=True)

    for path in CANADA_CROSSWALK_PATH.iterdir():
        if path.name not in CANADA_CROSSWALK_FILES:
            path.unlink()


####################################################
# Main
####################################################


def main():
    DOWNLOAD_LOG_PATH.unlink()
    shutil.rmtree(DATA_ROOT)
    DATA_ROOT.mkdir(exist_ok=True)

    download_bps_data()
    download_population_data()
    download_canada_crosswalk_data()


if __name__ == "__main__":
    main()
