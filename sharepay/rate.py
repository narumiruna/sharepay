from wise.rate import RateRequest

_store = {}


def query_rate(source: str, target: str) -> float:
    symbol = f"{source}/{target}"
    if symbol in _store:
        return _store[symbol]

    rate = RateRequest(source=source, target=target).do()
    _store[symbol] = rate.value
    return rate.value
