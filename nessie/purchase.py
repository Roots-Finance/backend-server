from .client import Nessie


class Purchase:
    client: Nessie

    id: str
    type: str
    merchant_id: str
    payer_id: str
    amount: float
    purchase_date: str
    status: str
    medium: str
    description: str

    def __init__(self, client: Nessie, **kwargs):
        """
        Constructor for the Purchase class.

        Args:
            client: The Nessie client instance.
        """
        self.client = client

        if all(key in kwargs for key in ["id", "type", "merchant_id", "payer_id"]):
            self.id = str(kwargs.get("id"))
            self.type = str(kwargs.get("type"))
            self.merchant_id = str(kwargs.get("merchant_id"))
            self.payer_id = str(kwargs.get("payer_id"))
            self.amount = float(str(kwargs.get("amount")))
            self.purchase_date = str(kwargs.get("purchase_date"))
            self.status = str(kwargs.get("status"))
            self.medium = str(kwargs.get("medium"))
        if "description" in kwargs:
            self.description = str(kwargs.get("description"))

    def __str__(self):
        return f"Purchase({self.id}, {self.type}, {self.merchant_id}, {self.payer_id}, {self.amount}, {self.purchase_date}, {self.status}, {self.medium}, {self.description})"
