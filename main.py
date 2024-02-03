from payshare import Currency
from payshare import Member
from payshare import Payment
from payshare import settle_up


def main() -> None:
    members = Member.from_names(["narumi", "dogiko", "ben", "john"])
    narumi = members["narumi"]
    dogiko = members["dogiko"]
    ben = members["ben"]
    john = members["john"]

    debts = []
    debts += Payment(
        amount=300,
        currency=Currency.JPY,
        payer=narumi,
        members=[narumi, dogiko, ben],
    ).debts()
    debts += Payment(amount=900, currency=Currency.JPY, payer=dogiko, members=[narumi, dogiko, ben]).debts()
    debts += Payment(amount=600, currency=Currency.JPY, payer=ben, members=[john, john]).debts()

    for d in debts:
        print(d)

    s = 0
    for _, v in members.items():
        s += v.balance
        print(v)
    assert s == 0

    settle_up(list(members.values()))


if __name__ == "__main__":
    main()
