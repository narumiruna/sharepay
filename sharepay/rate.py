from wise.rate import RateRequest


def query_rate(source: str, target: str) -> float:
    rate = RateRequest(source=source, target=target).do()
    return rate.value
