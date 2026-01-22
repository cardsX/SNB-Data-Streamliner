from io import BytesIO
import csv
import logging
from pathlib import Path
from random import random
from time import sleep
from types import TracebackType
from typing import Optional, Type
import requests
import pandas as pd


"""Examples of usage:

# In RAM dataset as dataframe
# ###########################
>>> cube = 'rendeiduebd'
>>> if not is_valid_cube_id(cube):
...     raise Exception(f"Error, '{cube}' invalid cube id.")
>>> v_level = 'v'
>>> with SNBDataEngine(logging_verbosity=v_level) as snb:
...     df = snb.download_to_dataframe(cube, selection="balsiscrevol")
...     if df is not None:
...         print(df.head())
         Date   D0  D1  Value
0  1988-01-01  CHF  1J    NaN
1  1988-01-01  CHF  2J    NaN
2  1988-01-01  CHF  3J    NaN
3  1988-01-01  CHF  4J    NaN
4  1988-01-01  CHF  5J    NaN

# Save to disk and then load to dataframe
# #######################################

# Case: single download
>>> cube = 'rendeiduebd'
>>> if not is_valid_cube_id(cube):
...     raise Exception(f"Error, '{cube}' invalid cube id.")
>>> v_level = 'v'
>>> with SNBDataEngine(logging_verbosity=v_level) as snb:
...     path = snb.download_to_file(cube, selection="balsiscrevol")
...     df = csv_to_dataframe(path)
...     if df is not None:
...         print(df.head())
         Date   D0  D1  Value
0  1988-01-01  CHF  1J    NaN
1  1988-01-01  CHF  2J    NaN
2  1988-01-01  CHF  3J    NaN
3  1988-01-01  CHF  4J    NaN
4  1988-01-01  CHF  5J    NaN

# Case: multiple downloads
>>> cubes = 'rendeiduebd', 'sddssbs14710q', 'contourisma', 'ambeschkla'
>>> valid_cubes = valid_cubes_ids()
>>> for cube in cubes:
...     if cube not in valid_cubes:
...         raise Exception(f"Error, '{cube}' invalid cube id.")
>>> v_level = 'v'
>>> with SNBDataEngine(logging_verbosity=v_level) as snb:
...     paths = snb.download_to_files(cubes, selection="balsiscrevol")
...     for path in paths:
...         ...
"""

# -- CONFIGURATION --
# -------------------
pwd = Path(__file__).resolve().parent # src directory
project_root = pwd.parent # root (project) directory

PATH_CUBES_LIST = project_root / "metadata" / "cubes_list.csv"


# -- DATASET VALIDATION--
# -----------------------
def valid_cubes_ids() -> list[str]:
    """Check the validity of the cube name among those supported by the SNB dataset API."""
    with open(PATH_CUBES_LIST, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        return next(zip(*reader))


def list_info_cubes() -> str:
    """Returns list of cubes with description"""
    with open(PATH_CUBES_LIST, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        # header
        column1, column2 = next(reader)
        # format output
        c1, c2 = zip(*reader)
        c1_size = len(max(c1, key=len))

        apply_row_template = f'{{:<{c1_size}}} {{}}'.format
        return (
            f'{apply_row_template(column1.title().replace("_", " "), column2.title())}\n'
            + '\n'.join(apply_row_template(_c1, c2[i]) for i, _c1 in enumerate(c1))
        )


def is_valid_cube_id(cube_id:str) -> bool:
    """Check the validity of the cube name among those supported by the SNB dataset API."""
    with open(PATH_CUBES_LIST, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        cube_ids, _ = zip(*reader)
        return cube_id in cube_ids


def csv_to_dataframe(path_csv:str, skiprows:int=2) -> pd.DataFrame:
    """Load the CVS-file to a Pandas dataframe."""
    file_path = Path(path_csv)
    if file_path.exists() and file_path.is_file():
        return pd.read_csv(file_path, sep=';', skiprows=skiprows, parse_dates=True)


# -- EXCEPTION --
# ---------------
class InvalidCubeIDError(Exception):
    """Exption is raised when an invalid cube id is detected. Check the function valid_cubes_ids or the command line python -m src --info for a detailed list of supported ids."""
    def __init__(self, cube_id, message="The given cube id is invalid"):
        self.cube_id = cube_id
        self.message = f"{message}: '{self.cube_id}'."
        super().__init__(self.message)


# -- EXTRACTOR --
# ---------------
class SNBDataEngine:
    """Download English CSV-cubes (dataset) from the SNB via API."""

    USER_AGENT = 'SNB-Analytics-Tool/1.0'

    def __init__(self, logging_verbosity=None):
        self.base_url = "https://data.snb.ch/api/cube" # <- hard-coded URL
        self.session:Optional[requests.Session] = None

        # set output verbosity
        self.logging_verbosity = logging_verbosity
        if logging_verbosity in {'v', 'V'}:
           # Possible output verbosity
            self._setup_logger(logging.INFO)
        elif logging_verbosity in {'vv', 'VV'}:
            self._setup_logger(logging.DEBUG)
        else:
            self.logging_verbosity = None

    def __enter__(self):
        """Initialize the session."""
        # manage the global TCP connection
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.USER_AGENT,
            'Accept': 'text/csv'
        })
        if self.logging_verbosity is not None:
            self.logger.info("[OK] SNB-session has started.")
        return self

    def __exit__(self,
                 exc_type:Optional[Type[BaseException]],
                 exc_val:Optional[BaseException],
                 exc_tb:Optional[TracebackType]):
        """On finishing close the session."""
        if self.session:
            self.session.close()
            if self.logging_verbosity is not None:
                self.logger.info("[OK] Session closed.")

    # --- CORE FUNCTION (Private) ---
    def _get_stream(self, cube_id:str, selection:Optional[str]=None, **config) -> requests.Response:
        """Manage the payload and return the streaming response object."""
        url = f"{self.base_url}/{cube_id}/data/csv/en"
        params = {'outputFormat': 'nonPivoted'} # <-hard-coded
        if selection:
            params['selectionConfigurations'] = f'selectionConfiguration,{selection}'
        
        return self.session.get(url, params=params | config, stream=True)

    def download_to_file(self, cube_id:str, selection:Optional[str]=None, folder="data/raw", **config) -> str:
        """Download the dataset (cube) and save it to disk. (Best suited for big dataset)"""
        path = Path(folder) / f"{cube_id}_{selection or 'all'}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_stream(cube_id, selection, **config) as r:
            if self.logging_verbosity is not None:
                self._audit_response(r)
            # Saving the stream content
            with open(path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=8192):
                    fd.write(chunk)

        if self.logging_verbosity:
            self.logger.info(f"[OK] cube saved at: '{path}'")

        return path

    def download_to_files(self, cubes_ids:list[str], selection:Optional[str]=None, folder="data/raw", **config) -> list[str]:
        """Download a list of datasets (cubes) sequentially and save them to disk. (Best suited for big dataset)"""
        # Sequential download
        paths = []
        for cube_id in cubes_ids:
            paths.append(
                    self.download_to_file(cube_id, selection=selection, folder=folder, **config)
            )
            # Pause the sequential download
            if len(cubes_ids) > 1:
                seconds = min(random()*5, 2) # <- hard-coded sleeptime between multiple downloads
                sleep(seconds)

        return paths

    def download_to_dataframe(self, cube_id:str, selection:Optional[str]=None, **config) -> pd.DataFrame:
        """Download the dataset (cube) in memory (RAM) by storing it in a Pandas DataFrame."""
        with self._get_stream(cube_id, selection, **config) as r:
            if self.logging_verbosity is not None:
                self._audit_response(r)
            df = pd.read_csv(BytesIO(r.content), sep=';', skiprows=2)

        if self.logging_verbosity:
            self.logger.info(f"[OK] cube stored in the DataFrame")
       
        return df

    def _setup_logger(self, level) -> None:
        self.logger = logging.getLogger("SNBEngine")
        # reset if already exist
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.setLevel(level)

        # console handler
        sh = logging.StreamHandler()
        sh.setLevel(level)

        # minimal formatting logging message
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        sh.setFormatter(formatter)

        self.logger.addHandler(sh)

    def _audit_response(self, response:requests.Response) -> None:
        """Details logging descriptions: info and debug."""
        
        # Format the size of the content
        raw_size = response.headers.get('Content-Length', '0')
        formatted_size = f"{int(raw_size):_}".replace('_', "'")
        
        # Logging standard (INFO)
        info_msg = f"""--- RESPONSE AUDIT ---
URL:          {response.url}
Status Code:  {response.status_code}
Content Type: {response.headers.get('Content-Type')}
Size:         {formatted_size} bytes"
""".strip('\n')
        self.logger.info(info_msg)
        
        # Logging DEBUG
        debug_msg = f"""Server:     {response.headers.get('Server')}
Date:         {response.headers.get('Date')}
Disposition:  {response.headers.get('content-disposition')}
Cookies:      {','.join(response.cookies.keys() if response.cookies else 'None')}
""".strip('\n')
        self.logger.debug(debug_msg)
