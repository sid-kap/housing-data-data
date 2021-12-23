# housing-data-data

Contains the data files used by [sid-kap/housing-data](https://github.com/sid-kap/housing-data). The Vercel build script downloads the data from this repo when building the site. We need to download them from the Census website and store them from GitHub, rather than downloading them directly in the build job, because the Census seems to be blocking downloads from AWS IPs.

## How to download data
Run the script `./download_data.py`. Your machine must have Python 3.10 installed.
