import concurrent
import json
import logging
import os
import datetime
from typing import List, Dict

from api.optionChainScanner import ChainScanner, ChainError
from utilities import contractUtilities

THREADS = 4
contractFileName = 'dataProcessing/contractStore.json'


def retrieveAndCleanData() -> Dict[str, List]:
    cleanedData = {}
    with open(contractFileName, 'r') as contractFile:
        contractDataFile = json.load(contractFile)
    for expiryDate in contractDataFile.keys():
        convertedExpiry = datetime.datetime.strptime(expiryDate, '%Y-%m-%d')
        if datetime.datetime.today() <= convertedExpiry:
            cleanedData[expiryDate] = contractDataFile[expiryDate]
    return cleanedData


def scrapeTicker(ticker: str) -> Dict[str, List]:
    chain = ChainScanner()
    chain.loadPage(ticker)
    try:
        dates = chain.getDates()
    except IndexError:
        logging.error(f'Symbol {ticker} has no option chain')
        return {'calls': [], 'puts': []}
    calls, puts = [], []
    for date in dates:
        chain.loadPage(ticker, date)
        try:
            callContracts, putContracts = chain.getContractNames()
            calls.extend(callContracts)
            puts.extend(putContracts)
        except ChainError as err:
            logging.error(f'{ticker} chain error: {err.errType}')
    return {'calls': calls, 'puts': puts}


def getContractMetaData(tickerNames: List[str], loadNewData=False):
    logging.info('Retrieving contract names')
    if loadNewData:
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            result = [res for res in executor.map(scrapeTicker, tickerNames.split(','))]
            storeData(result)
            return result
    else:
        return retrieveAndCleanData()


def storeData(contractData):
    data = {}
    for ticker in contractData:
        for call in ticker['calls']:
            date = contractUtilities.parseContractName(call)[1]
            dateString = date.strftime('%Y-%m-%d')
            if dateString in data:
                data[dateString]['calls'].append(call)
            else:
                data[dateString] = {
                    'calls': [call],
                    'puts': [],
                }
        for put in ticker['puts']:
            date = contractUtilities.parseContractName(put)[1]
            dateString = date.strftime('%Y-%m-%d')
            if dateString in data:
                data[dateString]['puts'].append(put)
            else:
                data[dateString] = {
                    'calls': [],
                    'puts': [put],
                }
    with open(contractFileName, 'w') as storage:
        json.dump(data, storage)
