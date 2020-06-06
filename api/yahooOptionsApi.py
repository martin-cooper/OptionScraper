import logging
from typing import List

from dataclasses import dataclass
from enum import Enum

from urllib3.exceptions import HTTPError
from requests.exceptions import ConnectionError
import requests
import time

from utilities.contractUtilities import parseContractName

BASE_URL = 'https://query1.finance.yahoo.com/v8/finance/chart/'
logging.basicConfig(level=logging.INFO)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

CONTRACT_REGEX = '([A-z]+)([0-9]+)([C|P])([0-9]+)'
MAX_RETRIES = 5


class DataGranularityPayload(Enum):
    INTRADAY = 'intraday'
    DAY = 'day'


@dataclass(repr=True)
class YahooOptionDatum:
    high: float
    low: float
    open: float
    close: float
    volume: int


class ContractData:
    def __init__(self, contractName, indicators):
        self.contractName = contractName
        self.ticker, self.date, self.contractType, self.strike = parseContractName(contractName)
        quote = indicators['quote'][0]
        self.data: List[YahooOptionDatum] = [
            YahooOptionDatum(datum,
                             quote['low'][count],
                             quote['open'][count],
                             quote['close'][count],
                             quote['volume'][count],
                             )
            for (count, datum) in enumerate(quote.get('high', []))]

    def __repr__(self):
        return str(self.__dict__)


class YahooOptionsApi:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = headers
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('https://', adapter)

    def execute(self, contractNames: List[str], dataRange: DataGranularityPayload) -> List[ContractData]:
        tickerData = []
        logging.info(f'Processing bundle starting with {contractNames[0]} and ending with {contractNames[-1]} with '
                     f'length {len(contractNames)}')
        elapsedTimes = []
        for contractName in contractNames:
            try:
                contractData, timeElapsed = self.getTickerData(contractName, dataRange)
                tickerData.append(contractData)
                elapsedTimes.append(timeElapsed)
                time.sleep(1)
            except HTTPError as err:
                logging.error(err.args)
        logging.info(f'Bundle starting with {contractNames[0]} and ending with {contractNames[-1]} took an '
                     f'average of {sum(elapsedTimes) / len(elapsedTimes)}s per request')
        return tickerData

    def getTickerData(self, contractName: str, dataRange: DataGranularityPayload, retries=0) -> ContractData:
        rangePayload = mapGranularityToPayload(dataRange)
        try:
            request = self.session.get(BASE_URL + contractName, params=rangePayload)
        except ConnectionError as e:
            logging.error(f'Connection error: for contract {contractName} {e.args}')
            if retries == MAX_RETRIES:
                raise e
            time.sleep(30)
            return self.getTickerData(contractName, dataRange, retries+1)
        data = request.json()
        if request.status_code != 200:
            raise HTTPError(f'Response code:{request.status_code}', request.url, request.reason, contractName)
        formattedData = ContractData(contractName, data['chart']['result'][0]['indicators'])
        # will likely run into issues without sleep
        return formattedData, request.elapsed.total_seconds()


def mapGranularityToPayload(dataRange: DataGranularityPayload):
    if dataRange == DataGranularityPayload.DAY:
        return {
            'interval': '1d',
            'range': '1d',
        }
    else:
        return {
            'interval': '1m',
            'range': '1d',
        }
