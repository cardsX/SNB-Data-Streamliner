import logging
from io import BytesIO
from pathlib import Path
from types import TracebackType
from typing import Optional, Type
import requests
import pandas as pd


"""Examples of usage:

# In RAM dataset as dataframe
# ###########################
>>> cube = 'rendeiduebd'
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
>>> cube = 'rendeiduebd'
>>> v_level = 'v'
>>> with SNBDataEngine(logging_verbosity=v_level) as snb:
...     path = snb.download_to_file(cube, selection="balsiscrevol")
...     file_path = Path(path)
...      if file_path.exists() and file_path.is_file():
...          df = pd.read_csv(file_path, sep=';', skiprows=2, parse_dates=True)
...          print(df.head())
         Date   D0  D1  Value
0  1988-01-01  CHF  1J    NaN
1  1988-01-01  CHF  2J    NaN
2  1988-01-01  CHF  3J    NaN
3  1988-01-01  CHF  4J    NaN
4  1988-01-01  CHF  5J    NaN
"""


class SNBDataEngine:
    """Download English csv-dataset from the SNB via API."""   
    def __init__(self, logging_verbosity=None):
        self.base_url = "https://data.snb.ch/api/cube"
        self.session:Optional[requests.Session] = None
    
        # set output verbosity
        self.logging_verbosity = logging_verbosity
        if logging_verbosity in {'v', 'v'}:
           # Possible output verbosity
            self._setup_logger(logging.INFO)
        elif logging_verbosity in {'vv', 'VV'}:
            self._setup_logger(logging.DEBUG)
        else:
            self.logging_verbosity = None
    
    def __enter__(self):
        """Initialise the session"""
        # manage the globale TCP connection
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SNB-Analytics-Tool/1.0', # <-hard-coded
            'Accept': 'text/csv'
        })
        if self.logging_verbosity is not None:
            pass#self.logger.info("[OK] SNB-session has started.")
        return self
        
    def __exit__(self,
                 exc_type:Optional[Type[BaseException]], 
                 exc_val:Optional[BaseException], 
                 exc_tb:Optional[TracebackType]):
        """On finishing close the sesion."""
        if self.session:
            self.session.close()
            if self.logging_verbosity is not None:
                pass#self.logger.info("[OK] Session closed.")

    # --- CORE FUNCTION (Private) ---
    def _get_stream(self, cube_id:str, selection:Optional[str]=None) -> requests.Response:
        """Manage the payload and return the streaming response object."""
        url = f"{self.base_url}/{cube_id}/data/csv/en"
        params = {'outputFormat': 'nonPivoted'} # <-hard-coded
        if selection:
            params['selectionConfigurations'] = f'selectionConfiguration,{selection}'
        
        return self.session.get(url, params=params, stream=True)

    def download_to_file(self, cube_id:str, selection:Optional[str]=None, folder="data/raw") -> str:
        """Download the dataset (cube) and save it to disk. (Best suited for big dataset)"""
        path = Path(folder) / f"{cube_id}_{selection or 'all'}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_stream(cube_id, selection) as r:
            if self.logging_verbosity is not None:
                self._audit_response(r)
            with open(path, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=8192):
                    fd.write(chunk)

        if self.logging_verbosity:
            self.logger.info(f"[OK] cube saved at: '{path}'")        

        return path
    
    def download_to_dataframe(self, cube_id:str, selection:Optional[str]=None) -> pd.DataFrame:
        """Download the dataset (cube) in memory (RAM) by storing it in a Pandas dataframe object."""
        with self._get_stream(cube_id, selection) as r:
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
        """Deatils logging descriptions: info and debug."""
        
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
