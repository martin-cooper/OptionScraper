import re
from datetime import date
from enum import Enum

CONTRACT_REGEX = '([A-z]+)([0-9]+)([C|P])([0-9]+)'


class OptionType(Enum):
    CALL = 'call'
    PUT = 'put'


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