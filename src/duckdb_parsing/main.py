import dataclasses

import duckdb


@dataclasses.dataclass
class Repayment:
    loan_id: int
    repayment_id: int
    amount: float
    paid: bool


@dataclasses.dataclass
class Loan:
    loan_id: int
    amount: float
    terms: int
    repayments: list[Repayment] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        repayment_amount = self.amount / self.terms
        for i in range(1, 1 + self.terms):
            self.repayments.append(
                Repayment(self.loan_id, i, repayment_amount, False)
            )


def main():
    loan = Loan(1, 1000, 10)

    # pay off three repayments
    for rep in loan.repayments[:3]:
        rep.paid = True

    # outstanding balance
    repayments = loan.repayments  # noqa: F841
    outstanding = duckdb.sql(
        """
        select sum(amount) as outstanding
        from repayments
        where loan_id = $id
          and paid = false
        """,
        params={"id": loan.loan_id},
    )
    print(outstanding)


def loan_repayments_as_csv(loan: Loan) -> str:
    csv = "loan_id,repayment_id,amount,paid\n"
    for repayment in loan.repayments:
        csv += f"{repayment.loan_id},{repayment.repayment_id},{repayment.amount},{repayment.paid}\n"

    return csv


def main_workaround():
    loan = Loan(1, 1000, 10)

    # pay off three repayments
    for rep in loan.repayments[:3]:
        rep.paid = True

    # outstanding balance  TODO: serialise to JSON instead -- performance difference?
    with open("repayments.csv", "w") as repayments_file:
        repayments_file.write(loan_repayments_as_csv(loan))

    repayments = duckdb.from_csv_auto(repayments_file.name, header=True)  # noqa: F841
    outstanding = duckdb.sql(
        """
        select sum(amount) as outstanding
        from repayments
        where loan_id = $id
          and paid = false
        """,
        params={"id": loan.loan_id},
    )
    print(outstanding)


if __name__ == "__main__":
    # main()
    main_workaround()
