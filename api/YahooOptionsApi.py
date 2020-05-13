from typing import List

from dataclasses import dataclass
from enum import Enum

from datetime import date
from urllib3.exceptions import HTTPError
import requests
import time

import re

BASE_URL = 'https://query1.finance.yahoo.com/v8/finance/chart/'

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


class DataGranularityPayload(Enum):
    INTRADAY = 'intraday'
    DAY = 'day'


class OptionType(Enum):
    CALL = 'call'
    PUT = 'put'


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
        self.ticker, self.date, self.contractType, self.strike = self.parseContractName(contractName)
        quote = indicators['quote'][0]
        self.data: List[YahooOptionDatum] = [
            YahooOptionDatum(datum,
                             quote['low'][count],
                             quote['open'][count],
                             quote['close'][count],
                             quote['volume'][count],
                             )
            for (count, datum) in enumerate(quote.get('high', []))]

    @staticmethod
    def parseContractName(contractName):
        contractName = re.search(CONTRACT_REGEX, contractName)
        if contractName:
            ticker = contractName.group(1)

            contractDateRaw = contractName.group(2)
            contractYear = int(contractDateRaw[:2]) + 2000
            contractMonth = int(contractDateRaw[2:4])
            contractDay = int(contractDateRaw[4:])
            contractDateObj = date(contractYear, contractMonth, contractDay)

            contractType = OptionType.CALL if contractName.group(3) == 'C' else OptionType.PUT
            strikeRaw = contractName.group(4)
            strikeConverted = float(f'{strikeRaw[:-3]}.{strikeRaw[-3:]}')

        return ticker, contractDateObj, contractType, strikeConverted

    def __repr__(self):
        return f'''
        {{
            contract name: {self.contractName}
            ticker: {self.ticker}
            expiry: {self.date}
            strike: {self.strike}
            type: {self.contractType}
            data: {self.data}
        }}
        '''


class YahooOptionsApi:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = headers

    def execute(self, contractNames: List[str], dataRange: DataGranularityPayload) -> List[ContractData]:
        optionData = []
        for (count, contract) in enumerate(contractNames):
            try:
                tickerData = self.getTickerData(contract, dataRange)
                optionData.append(tickerData)
            except HTTPError as err:
                print(err.args)

        return optionData

    def getTickerData(self, contractName: str, dataRange: DataGranularityPayload) -> ContractData:
        rangePayload = mapGranularityToPayload(dataRange)
        request = self.session.get(BASE_URL + contractName, params=rangePayload)
        data = request.json()
        if request.status_code != 200:
            raise HTTPError(f'Response code:{request.status_code}', request.url, request.reason, contractName)
        formattedData = ContractData(contractName, data['chart']['result'][0]['indicators'])
        # will likely run into issues without sleep
        time.sleep(0.25)
        return formattedData


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
