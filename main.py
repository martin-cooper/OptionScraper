import concurrent.futures
import logging
import random
import time
from typing import List, Dict

from api.yahooOptionsApi import YahooOptionsApi, DataGranularityPayload
from dataProcessing import optionChainProcessor

logging.basicConfig(level=logging.ERROR)
NASDAQ = "ATVI,ADBE,AMD,ALXN,ALGN,GOOG,GOOGL,AMZN,AMGN,ADI,ANSS,AAPL,AMAT,ASML,ADSK,ADP,BIDU,BIIB,BMRN,BKNG,AVGO," \
         "CDNS,CDW,CERN,CHTR,CHKP,CTAS,CSCO,CTXS,CTSH,CMCSA,CPRT,CSGP,COST,CSX,DXCM,DLTR,EBAY,EA,EXC,EXPE,FB,FAST," \
         "FISV,FOX,FOXA,GILD,IDXX,ILMN,INCY,INTC,INTU,ISRG,JD,KLAC,LRCX,LBTYA,LBTYK,LULU,MAR,MXIM,MELI,MCHP,MU,MSFT," \
         "MDLZ,MNST,NTAP,NTES,NFLX,NVDA,NXPI,ORLY,PCAR,PAYX,PYPL,PEP,QCOM,REGN,ROST,SGEN,SIRI,SWKS,SPLK,SBUX,SNPS," \
         "TMUS,TTWO,TSLA,TXN,KHC,TCOM,ULTA,UAL,VRSN,VRSK,VRTX,WBA,WDC,WDAY,XEL,XLNX,ZM"
CONTRACT_NAME_SIZE = 200


def chunkList(data: List, chunkSize: int) -> List[List]:
    return [data[i: i + chunkSize] for i in range(0, len(data), chunkSize)]


def aggregateAndNormalizeContractNames(contractNames: List[Dict[str, str]]) -> List[List[str]]:
    aggregated = []
    for contractList in contractNames:
        calls = contractList['calls']
        puts = contractList['puts']
        aggregated.extend(calls + puts)
    normalized = chunkList(aggregated, CONTRACT_NAME_SIZE)
    return random.shuffle(normalized)


def queryData(contractNames: List[str]):
    yahoo = YahooOptionsApi()
    return yahoo.execute(contractNames, DataGranularityPayload.INTRADAY)


def getContractPricingData(contractNames: List[Dict[str, str]]):
    THREADS = 30
    contracts = aggregateAndNormalizeContractNames(contractNames)
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        result = [res for res in executor.map(queryData, contracts)]
        return result


def main():
    logging.info('Starting program')
    startTime = time.time()
    (optionChainProcessor.getContractMetaData(NASDAQ, loadNewData=False))
    logging.info(f'Process finished in {time.time() - startTime} seconds')


main()
