from enum import Enum


class AccountType(Enum):
    CHECKING = "Checking"
    SAVINGS = "Savings"
    CREDIT_CARD = "Credit Card"

    def __str__(self):
        return self.value
