import pprint

from api.YahooOptionsApi import YahooOptionsApi, DataGranularityPayload
from api.OptionChainScanner import ChainScanner

chain = ChainScanner()
chain.loadPage('TSLA')
dates = chain.getDates()

callContracts, putContracts = chain.getContractNames()

optionData = YahooOptionsApi()
(optionData.execute(callContracts, DataGranularityPayload.INTRADAY))
