import random
from typing import List

from . import Account, Nessie
from .types import AccountType


class Customer:
    client: Nessie
    id: str
    first_name: str
    last_name: str
    street_number: str
    street_name: str
    city: str
    state: str
    zip_code: str
    accounts: List[Account]

    def __init__(self, client: Nessie, **kwargs):
        """
        Constructor for the Customer class.

        Args:
            client: The Nessie client instance.
        """
        self.client = client
        if all(
            key in kwargs
            for key in [
                "first_name",
                "last_name",
                "street_number",
                "street_name",
                "city",
                "state",
                "zip_code",
            ]
        ):
            self.first_name = str(kwargs.get("first_name"))
            self.last_name = str(kwargs.get("last_name"))
            self.street_number = str(kwargs.get("street_number"))
            self.street_name = str(kwargs.get("street_name"))
            self.city = str(kwargs.get("city"))
            self.state = str(kwargs.get("state"))
            self.zip_code = str(kwargs.get("zip_code"))
        if "id" in kwargs:
            self.id = str(kwargs.get("id"))
            self.accounts = self.get_accounts()

    def create(self):
        """
        Creates a new customer.
        """
        response = self.client.post(
            "/customers",
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "address": {
                    "street_number": self.street_number,
                    "street_name": self.street_name,
                    "city": self.city,
                    "state": self.state,
                    "zip": self.zip_code,
                },
            },
        )

        print(response.json())
        self.id = response.json()["objectCreated"]["_id"]

    def update(self, **kwargs):
        """
        Updates a customer.

        Args:
            **kwargs: Keyword arguments to update the customer.
        """
        first_name = kwargs.get("first_name", self.first_name)
        last_name = kwargs.get("last_name", self.last_name)
        street_number = kwargs.get("street_number", self.street_number)
        street_name = kwargs.get("street_name", self.street_name)
        city = kwargs.get("city", self.city)
        state = kwargs.get("state", self.state)
        zip_code = kwargs.get("zip_code", self.zip_code)

        self.client.put(
            f"/customers/{self.id}",
            {
                "first_name": first_name,
                "last_name": last_name,
                "address": {
                    "street_number": street_number,
                    "street_name": street_name,
                    "city": city,
                    "state": state,
                    "zip": zip_code,
                },
            },
        )

    def get_accounts(self) -> List[Account]:
        """
        Returns a list of all accounts for the customer.

        Returns:
            A list of all accounts for the customer.
        """
        account_json = self.client.get(f"/customers/{self.id}/accounts").json()

        account_objs = []

        for _account in account_json:
            account_objs.append(
                Account(
                    self.client,
                    id=_account["_id"],
                    type=_account["type"],
                    nickname=_account["nickname"],
                    rewards=_account["rewards"],
                    balance=_account["balance"],
                    customer_id=_account["customer_id"],
                )
            )
        return account_objs

    def open_account(self, account_type: AccountType, nickname: str) -> Account:
        """
        Opens a new account for the customer.

        Args:
            account_type: The type of account to open.
            nickname: The nickname for the account.

        Returns:
            A new account for the customer.
        """
        account_number = str(random.randint(1000000000, 9999999999))
        account_json = self.client.post(
            f"/customers/{self.id}/accounts",
            {
                "type": str(account_type),
                "nickname": f"{nickname} | {account_number}",
                "rewards": 0,
                "balance": 0,
            },
        ).json()
        account_json = account_json["objectCreated"]
        return Account(
            self.client,
            id=account_json["_id"],
            type=account_json["type"],
            nickname=account_json["nickname"],
            rewards=account_json["rewards"],
            balance=account_json["balance"],
            customer_id=account_json["customer_id"],
        )
