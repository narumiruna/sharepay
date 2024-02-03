import copy

from .member import Member


def settle_up(members: list[Member] | dict[str, Member]) -> None:
    if isinstance(members, dict):
        members = list(members.values())

    members = copy.deepcopy(members)

    while len(members) > 1:
        members = sorted(members, key=lambda x: -x.balance)

        richest = members[0]
        poorest = members.pop()
        amount = poorest.balance

        print(f"{poorest.name: <6} 匯給 {richest.name: <6} {-amount: >10.2f} TWD")
        richest.balance += amount
