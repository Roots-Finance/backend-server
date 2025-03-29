from typing import List

from .client import Nessie
from .customer import Customer


class CustomerManager:
    client: Nessie

    def __init__(self, client: Nessie):
        """
        Constructor for the CustomerManager class.

        Args:
            client: The Nessie client instance.
        """
        self.client = client

    def get_customers(self) -> List[Customer]:
        """
        Returns a list of all customers.

        Returns:
            A list of all customers.
        """
        customer_json = self.client.get("/customers").json()

        customer_objs = []

        for _customer in customer_json:
            customer_objs.append(
                Customer(
                    self.client,
                    id=_customer["_id"],
                    first_name=_customer["first_name"],
                    last_name=_customer["last_name"],
                    street_number=_customer["address"]["street_number"],
                    street_name=_customer["address"]["street_name"],
                    city=_customer["address"]["city"],
                    state=_customer["address"]["state"],
                    zip_code=_customer["address"]["zip"],
                )
            )

        return customer_objs

    def get_customer(self, id: str) -> Customer:
        """
        Returns a customer by id.

        Args:
            id: The id of the customer.

        Returns:
            A customer object.
        """
        customer_json = self.client.get(f"/customers/{id}").json()

        return Customer(
            self.client,
            id=customer_json["_id"],
            first_name=customer_json["first_name"],
            last_name=customer_json["last_name"],
            street_number=customer_json["address"]["street_number"],
            street_name=customer_json["address"]["street_name"],
            city=customer_json["address"]["city"],
            state=customer_json["address"]["state"],
            zip_code=customer_json["address"]["zip"],
        )
