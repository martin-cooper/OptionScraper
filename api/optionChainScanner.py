import time
import logging

from datetime import date
from typing import Tuple, List

from bs4 import BeautifulSoup
import requests
import pandas as pd
from requests import Response

BASE_URL = 'https://finance.yahoo.com/quote'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/83.0.4103.61 Safari/537.36'
}


class ChainError(Exception):
    def __init__(self, errType):
        self.errType = errType


class ChainScanner:
    def __init__(self):
        session = requests.Session()
        session.headers = headers
        self.session = session
        self.soup: BeautifulSoup = None

    def loadPage(self, ticker, expiry=None) -> None:
        url = f'{BASE_URL}/{ticker}/options'
        startLoad = time.time()
        logging.info(f'Loading chain for ticker {ticker} and date {date.fromtimestamp(expiry) if expiry else None}')
        page: Response = self.session.get(url) if not expiry \
            else self.session.request('GET', url, {'date': expiry})
        logging.info(f'Chain loaded for {ticker} with date {date.fromtimestamp(expiry) if expiry else None}'
                     f' in {time.time() - startLoad} seconds')
        self.soup: BeautifulSoup = BeautifulSoup(page.content, 'lxml')

    def getContractNames(self) -> Tuple[List[str], List[str]]:
        tables = self.soup.find_all('table')
        pandaTables: List[List[pd.DataFrame]] = [pd.read_html(str(table)) for table in tables]
        if len(pandaTables) != 2:
            raise ChainError('Missing either put or call chain')
        callTable: pd.DataFrame = pandaTables[0][0]
        callContractNames = callTable['Contract Name'].to_list()

        putTable: pd.DataFrame = pandaTables[1][0]
        putContractNames = putTable['Contract Name'].to_list()

        return callContractNames, putContractNames

    def getDates(self):
        dates = self.soup.find_all('select', {'class': 'Fz(s)'})
        datesSelector = dates[0].contents
        datesAsSeconds = [int(timeStamp.attrs['value']) for timeStamp in datesSelector]
        return datesAsSeconds
