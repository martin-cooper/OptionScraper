import time
import concurrent.futures

from api.YahooOptionsApi import YahooOptionsApi, DataGranularityPayload
from api.OptionChainScanner import ChainScanner, ChainError


NASDAQ = "ATVI,ADBE,AMD,ALXN,ALGN,GOOG,GOOGL,AMZN,AMGN,ADI,ANSS,AAPL,AMAT,ASML,ADSK,ADP,BIDU,BIIB,BMRN,BKNG,AVGO," \
         "CDNS,CDW,CERN,CHTR,CHKP,CTAS,CSCO,CTXS,CTSH,CMCSA,CPRT,CSGP,COST,CSX,DXCM,DLTR,EBAY,EA,EXC,EXPE,FB,FAST," \
         "FISV,FOX,FOXA,GILD,IDXX,ILMN,INCY,INTC,INTU,ISRG,JD,KLAC,LRCX,LBTYA,LBTYK,LULU,MAR,MXIM,MELI,MCHP,MU,MSFT," \
         "MDLZ,MNST,NTAP,NTES,NFLX,NVDA,NXPI,ORLY,PCAR,PAYX,PYPL,PEP,QCOM,REGN,ROST,SGEN,SIRI,SWKS,SPLK,SBUX,SNPS," \
         "TMUS,TTWO,TSLA,TXN,KHC,TCOM,ULTA,UAL,VRSN,VRSK,VRTX,WBA,WDC,WDAY,XEL,XLNX,ZM"


def scrapeTicker(ticker: str) -> None:
    chain = ChainScanner()
    optionData = YahooOptionsApi()
    chain.loadPage(ticker)
    dates = chain.getDates()
    firstDate = dates[0]
    chain.loadPage(ticker, firstDate)
    try:
        dataQueryStart = time.time()
        callContracts, putContracts = chain.getContractNames()
        optionData.execute(callContracts, DataGranularityPayload.INTRADAY)
        queryEnd = time.time()
        print(f'Data query for {ticker} took {queryEnd - dataQueryStart} seconds')
    except ChainError as err:
        print(f'{ticker} chain error; {err.errType}')


def getOptionData():
    THREADS = 103
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.map(scrapeTicker, NASDAQ.split(','))


startTime = time.time()
getOptionData()
print(time.time() - startTime)
