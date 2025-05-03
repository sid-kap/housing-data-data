#! /usr/bin/env python3.10
import shutil
from pathlib import Path
from subprocess import Popen, run
from tempfile import NamedTemporaryFile

DATA_ROOT = Path("./data")
DOWNLOAD_LOG_PATH = Path("download.log")


def download_to_directory(url: str, output_dir: Path) -> Popen:
    # Downloads async (in parallel)
    output_dir.mkdir(parents=True, exist_ok=True)
    return Popen(["wget", url, "-P", str(output_dir), "-a", DOWNLOAD_LOG_PATH])


####################################################
# BPS downloading functions
####################################################


REGIONS = [
    ("so", "South Region"),
    ("ne", "Northeast Region"),
    ("we", "West Region"),
    ("mw", "Midwest Region"),
]
BPS_PREFIX = "https://www2.census.gov/econ/bps/"

LATEST_MONTH = (2025, 3)

# Whether to download the monthly files from December of the latest full year of data available.
# This is needed in Jan-May of each year, because the full year's estimates (imputing the
# small counties that don't get surveyed every month) for the previous year don't come out until
# May.
# Arguably, we could just always download the December estimate for the previous year, even if it's
# not strictly needed. But let's do this for now, can revisit later.
GET_PREVIOUS_YEAR_DECEMBER_MONTHLY_DATA = True
PREVIOUS_YEAR = 2024


def get_place_path(
    year_or_year_month: int, region_tuple: tuple[str, str], frequency: str = "a"
) -> str:
    return f"Place/{region_tuple[1]}/{region_tuple[0]}{year_or_year_month:04d}{frequency}.txt"


def get_county_path(year_or_year_month: int, frequency: str = "a") -> str:
    return f"County/co{year_or_year_month:04d}{frequency}.txt"


def get_state_path(year_or_year_month: int, frequency: str = "a") -> str:
    return f"State/st{year_or_year_month:04d}{frequency}.txt"


def download_bps_data() -> None:
    paths = []

    max_annual_year = (
        PREVIOUS_YEAR if GET_PREVIOUS_YEAR_DECEMBER_MONTHLY_DATA else PREVIOUS_YEAR + 1
    )
    for year in range(1980, max_annual_year):
        for region_tuple in REGIONS:
            paths.append(get_place_path(year, region_tuple))
        if year >= 1990:
            paths.append(get_county_path(year))
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
        paths.append(get_state_path(latest_year_month, frequency="y"))

    for path in paths:
        output_dir = Path(DATA_ROOT, "bps", path).parent
        download_to_directory(BPS_PREFIX + path, output_dir)


####################################################
# California APR downloading functions
####################################################


def download_california_apr_data() -> None:
    process = download_to_directory(
        "https://data.ca.gov/dataset/81b0841f-2802-403e-b48e-2ef4b751f77c/resource/fe505d9b-8c36-42ba-ba30-08bc4f34e022/download/table-a2-combined.csv",
        Path(DATA_ROOT, "apr"),
    )
    process.wait()
    # gzip the file so that it's under GitHub's 100MB limit
    run(
        ["gzip", "-f", str(Path(DATA_ROOT, "apr", "table-a2-combined.csv"))], check=True
    )


####################################################
# Census crosswalks
####################################################

CROSSWALK_DIR = Path(DATA_ROOT, "crosswalk")


def download_census_crosswalk_data() -> None:
    download_to_directory(
        "https://www2.census.gov/programs-surveys/popest/geographies/2021/all-geocodes-v2021.xlsx",
        CROSSWALK_DIR,
    )
    download_to_directory(
        "http://data.nber.org/cbsa-csa-fips-county-crosswalk/cbsa2fipsxw.csv",
        CROSSWALK_DIR,
    )


####################################################
# Census population downloading functions
####################################################

STATE_POPULATION_PATHS = [
    "https://www2.census.gov/programs-surveys/popest/tables/1980-1990/state/asrh/st8090ts.txt",
    "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/state/totals/nst-est2020-alldata.csv",
    "https://www2.census.gov/programs-surveys/popest/datasets/2020-2023/state/totals/NST-EST2023-ALLDATA.csv",
    "https://www2.census.gov/programs-surveys/popest/tables/2000-2010/intercensal/state/st-est00int-01.xls",
] + [
    f"https://www2.census.gov/programs-surveys/popest/tables/1990-2000/intercensal/st-co/stch-icen{year}.txt"
    for year in range(1990, 2000)
]

COUNTY_POPULATION_PATHS = (
    [
        "https://www2.census.gov/programs-surveys/popest/tables/1990-2000/counties/totals/99c8_00.txt",
        "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/co-est2020-alldata.csv",
        "https://www2.census.gov/programs-surveys/popest/datasets/2020-2023/counties/totals/co-est2023-alldata.csv",
    ]
    + [
        f"https://www2.census.gov/programs-surveys/popest/tables/2000-2010/intercensal/county/co-est00int-01-{state_fips:02d}.csv"
        # Not sure why the state fips are this weird series rather than just 1 through 50.
        for state_fips in range(1, 57)
        if state_fips not in {3, 7, 14, 43, 52}
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
    "https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/cities/SUB-EST2020_ALL.csv",
    "https://www2.census.gov/programs-surveys/popest/datasets/2020-2022/cities/totals/sub-est2022.csv",
]

POPULATION_ROOT = Path(DATA_ROOT, "population")
STATE_POPULATION_ROOT = Path(POPULATION_ROOT, "state")
COUNTY_POPULATION_ROOT = Path(POPULATION_ROOT, "county")
PLACE_POPULATION_ROOT = Path(POPULATION_ROOT, "place")


def download_population_data() -> None:
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
CANADA_POPULATION_PATH = Path(DATA_ROOT, "canada-population")


CANADA_CROSSWALK_FILES = [
    "CSD.csv",
    "CD.csv",
    "PR.csv",
    "CMA_CA.csv",
]


def _download_zip(url: str, out_folder_path: Path) -> None:
    """
    Downloads a zip and unzips its contents into a folder at `out_folder_path`
    (which shouldn't exist before calling this function).
    """
    with NamedTemporaryFile() as temp_file:
        run(["wget", url, "-O", temp_file.name, "-a", DOWNLOAD_LOG_PATH], check=True)
        # e unzips all files directly into the folder, regardless of their true path.
        # Seems fine for these zips where we don't know or care if there's a wrapper folder
        # all the files we care about are flat
        run(["7z", "e", temp_file.name, f"-o{out_folder_path}"], check=True)


def download_canada_crosswalk_data() -> None:
    _download_zip(
        "https://www12.statcan.gc.ca/census-recensement/2021/geo/aip-pia/geosuite/files-fichiers/2021_92-150-X_eng.zip",
        CANADA_CROSSWALK_PATH,
    )

    for path in CANADA_CROSSWALK_PATH.iterdir():
        if path.name not in CANADA_CROSSWALK_FILES:
            # 7z e dumps the dirs too as empty dirs in the same folder
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()


def download_canada_population_data() -> None:
    _download_zip(
        "https://www150.statcan.gc.ca/n1/tbl/csv/17100142-eng.zip",
        CANADA_POPULATION_PATH,
    )


####################################################
# Main
####################################################


def main() -> None:
    DOWNLOAD_LOG_PATH.unlink(missing_ok=True)
    shutil.rmtree(DATA_ROOT)
    DATA_ROOT.mkdir(exist_ok=True)

    download_bps_data()
    download_california_apr_data()
    download_census_crosswalk_data()
    download_population_data()
    download_canada_crosswalk_data()
    download_canada_population_data()


if __name__ == "__main__":
    main()
