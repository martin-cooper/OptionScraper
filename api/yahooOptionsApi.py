import logging
from typing import List

from urllib3.exceptions import HTTPError
from requests.exceptions import ConnectionError
import requests
import datetime
import time

from data.contractData import ContractData

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


class YahooOptionsApi:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = headers
        adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount('https://', adapter)

    def execute(self, contractNames: List[str]) -> List[ContractData]:
        tickerData = []
        logging.info(f'Processing bundle starting with {contractNames[0]} and ending with {contractNames[-1]} with '
                     f'length {len(contractNames)}')
        elapsedTimes = []
        for contractName in contractNames:
            try:
                contractData, timeElapsed = self.getTickerData(contractName)
                if contractData is not None:
                    tickerData.append(contractData)
                elapsedTimes.append(timeElapsed)
                time.sleep(1)
            except HTTPError as err:
                logging.error(err.args)
        logging.info(f'Bundle starting with {contractNames[0]} and ending with {contractNames[-1]} took an '
                     f'average of {sum(elapsedTimes) / len(elapsedTimes)}s per request')
        return tickerData

    def getTickerData(self, contractName: str, retries=0) -> ContractData:
        params = getStartAndEndTimeStamps()
        try:
            request = self.session.get(BASE_URL + contractName, params=params)
        except ConnectionError as e:
            logging.error(f'Connection error: for contract {contractName} {e.args}')
            if retries == MAX_RETRIES:
                raise e
            time.sleep(30)
            return self.getTickerData(contractName, retries + 1)
        data = request.json()
        if request.status_code != 200:
            raise HTTPError(f'Response code:{request.status_code}', request.url, request.reason, contractName)
        result = data['chart']['result'][0]
        if 'timestamp' not in result:
            return None, request.elapsed.total_seconds()
        formattedData = ContractData(contractName, result['indicators'], result['timestamp'])
        return formattedData, request.elapsed.total_seconds()


def getStartAndEndTimeStamps():
    dayStart = datetime.datetime.combine(datetime.date.today(), datetime.time()).timestamp()
    dayEnd = datetime.datetime.combine(datetime.date.today(), datetime.time(hour=23, minute=59)).timestamp()
    return {
        'period1': int(dayStart),
        'period2': int(dayEnd),
        'interval': '1m',
    }
