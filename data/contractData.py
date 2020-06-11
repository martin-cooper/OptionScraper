from dataclasses import dataclass
from typing import List

from utilities.contractUtilities import parseContractName


@dataclass(repr=True)
class YahooOptionDatum:
    contractName: str
    high: float
    low: float
    open: float
    close: float
    volume: int
    timestamp: int


class ContractData:
    def __init__(self, contractName, indicators, timestamps):
        self.contractName = contractName
        self.ticker, self.date, self.contractType, self.strike = parseContractName(contractName)
        quote = indicators['quote'][0]
        self.data: List[YahooOptionDatum] = []
        for count, datum in enumerate(quote.get('high', [])):
            dataPoint = YahooOptionDatum(contractName,
                                         datum,
                                         quote['low'][count],
                                         quote['open'][count],
                                         quote['close'][count],
                                         quote['volume'][count],
                                         timestamps[count]
                                         )
            if dataPoint.volume is not None and dataPoint.volume > 0:
                self.data.append(dataPoint)

    def __repr__(self):
        return str(self.__dict__)
