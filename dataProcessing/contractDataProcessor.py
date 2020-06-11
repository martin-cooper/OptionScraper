import concurrent.futures
import random
from typing import List, Dict

from api.yahooOptionsApi import YahooOptionsApi

CONTRACT_NAME_SIZE = 200
THREADS = 200


def chunkList(data: List, chunkSize: int) -> List[List]:
    return [data[i: i + chunkSize] for i in range(0, len(data), chunkSize)]


def aggregateAndNormalizeContractNames(contractNames: List[Dict[str, List[str]]]) -> List[List[str]]:
    aggregated = []
    for contractList in contractNames:
        calls = contractList['calls']
        puts = contractList['puts']
        aggregated.extend(calls + puts)
    normalized = chunkList(aggregated, CONTRACT_NAME_SIZE)
    random.shuffle(normalized)
    return normalized


def queryData(contractNames: List[str]):
    yahoo = YahooOptionsApi()
    return yahoo.execute(contractNames)


def getContractPricingData(contractNames: List[Dict[str, str]]):
    contracts = aggregateAndNormalizeContractNames(contractNames)
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        result = [res for res in executor.map(queryData, contracts)]
        aggregated = []
        for contractList in result:
            aggregated.extend(contractList)
        return aggregated
