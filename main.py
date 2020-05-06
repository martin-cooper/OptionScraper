import pprint

from api.YahooOptionsApi import YahooOptionsApi, DataGranularityPayload
from api.OptionChainScanner import ChainScanner

chain = ChainScanner()
chain.loadPage('TSLA')
dates = chain.getDates()

callContracts, putContracts = chain.getContractNames()

optionData = YahooOptionsApi()
pprint.pprint(optionData.execute(callContracts, DataGranularityPayload.DAY))
