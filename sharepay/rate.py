from wise.rate import RateRequest

STORE = {}


def query_rate(source: str, target: str) -> float:
    symbol = f"{source}/{target}"
    if symbol in STORE:
        return STORE[symbol]

    rate = RateRequest(source=source, target=target).do()
    STORE[symbol] = rate.value
    return rate.value
