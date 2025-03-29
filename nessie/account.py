from typing import List

from .client import Nessie
from .purchase import Purchase
from .types.account_type import AccountType


class Account:
    client: Nessie
    id: str
    type: AccountType
    nickname: str
    rewards: float
    balance: float
    account_number: str
    customer_id: str
    purchases: List[Purchase]

    def __init__(self, client: Nessie, **kwargs):
        """
        Constructor for the Account class.

        Args:
            client: The Nessie client instance.
        """
        self.client = client

        if all(key in kwargs for key in ["id", "type", "nickname", "rewards"]):
            self.id = str(kwargs.get("id"))
            self.type = AccountType(kwargs.get("type"))
            self.nickname = str(kwargs.get("nickname"))
            self.rewards = float(str(kwargs.get("rewards")))
            self.balance = float(str(kwargs.get("balance")))
            self.account_number = str(kwargs.get("account_number"))
            self.customer_id = str(kwargs.get("customer_id"))
            self.purchases = self.get_purchases()

    def rename(self, nickname: str):
        """
        Renames the account.

        Args:
            nickname: The new nickname for the account.
        """
        self.client.put(
            f"/accounts/{self.id}",
            {"nickname": nickname, "account_number": self.account_number},
        )

    def get_purchases(self) -> List[Purchase]:
        """
        Returns a list of all purchases for the account.

        Returns:
            A list of all purchases for the account.
        """

        purchase_json = self.client.get(f"/accounts/{self.id}/purchases").json()

        purchase_objs = []

        for _purchase in purchase_json:
            purchase_objs.append(
                Purchase(
                    self.client,
                    id=_purchase["_id"],
                    type=_purchase["type"],
                    merchant_id=_purchase["merchant_id"],
                    payer_id=_purchase["payer_id"],
                    amount=_purchase["amount"],
                    purchase_date=_purchase["purchase_date"],
                    status=_purchase["status"],
                    medium=_purchase["medium"],
                    description=_purchase["description"],
                )
            )

        return purchase_objs
