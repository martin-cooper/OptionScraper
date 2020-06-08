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


def main():
    logging.info('Starting program')
    startTime = time.time()
    (optionChainProcessor.getContractMetaData(NASDAQ, loadNewData=False))
    logging.info(f'Process finished in {time.time() - startTime} seconds')


main()
