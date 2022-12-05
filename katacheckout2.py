from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Tuple
from decimal import Decimal


@dataclass
class SKU:
    """Single unit of product, defined by price and name"""

    name: str
    price: Decimal

    def __init__(self, name: str, price: Union[float, int, str]) -> None:
        self.name = name
        self.price = Decimal(price)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, type(self)) and self.name == other.name:
            return True
        if isinstance(other, str) and self.name == other:
            return True

        return False


@dataclass
class Item(SKU):
    """an item is an SKU with a quantity attached"""

    quantity: int

    def __init__(self, name: str, price: Union[float, int, str], quantity: int) -> None:
        super().__init__(name, price)
        self.quantity = quantity

    def __hash__(self) -> int:
        return super().__hash__()

    def __eq__(self, other):
        return super().__eq__(other)


class Basket:
    """set of items"""

    items: Dict[SKU, int]

    def __init__(self, items: Dict[SKU, int] = None) -> None:
        if items is None:
            self.items = {}
        else:
            self.items = items

    def add(self, item: Item) -> None:
        """add item to the basket"""
        if item in self.items:
            self.items[item] = self.items[item] + item.quantity
        else:
            self.items[item] = item.quantity

    def get_items(self):
        """get all items"""
        return self.items


@dataclass
class SpecialOffer(SKU):
    """special offer, include a name"""

    offer_name: str
    quantity: int

    def __init__(
        self,
        name: str,
        price: Union[float, int, str],
        quantity: int,
        offer_name: str = "",
    ) -> None:
        super().__init__(name, price)
        self.offer_name = offer_name
        self.quantity = quantity

    def times(self, quantity: int) -> int:
        """evaluate how many times the offer is applied"""
        return int(quantity / self.quantity)

    def evaluate_price(self, quantity: int) -> Decimal:
        """evaluate the price for the offer"""
        return self.times(quantity) * self.price

    def residual(self, quantity: int) -> int:
        """calculate residuals that aren't included in an offer"""
        return quantity % self.quantity


class Order:
    """final order"""

    items: List[Item]
    offers_applied: List[Tuple[SpecialOffer, int]]
    total: Decimal = Decimal(0)
    partials: Dict[SKU, Decimal]

    def __init__(self) -> None:
        self.items = []
        self.offers_applied = []
        self.total = Decimal(0)
        self.partials = {}

    def add_item(self, item: Item):
        """record item"""
        self.items.append(item)

    def include_offer(self, offer: SpecialOffer, times: int = 1):
        """include an offer in the order"""
        self.offers_applied.append(
            (
                offer,
                times,
            )
        )

    def get_partials(self, key: Union[SKU, str]) -> Decimal:
        """get the partial order"""
        # they map on the same hash
        return self.partials[key]


class CheckOut:
    """checkout system"""

    offers: List[SpecialOffer]

    def __init__(self) -> None:
        self.offers = []

    def register_offer(self, offer: SpecialOffer):
        """register offer in the checkout system"""
        self.offers.append(offer)

    def lookup_offer(self, item: SKU) -> Optional[SpecialOffer]:
        """check if there is an offer for the item"""
        for offer in self.offers:
            if offer.name == item.name:
                return offer

        return None

    def evaluate_partial(
        self, item: Item, quantity: int
    ) -> Tuple[Decimal, Optional[SpecialOffer]]:
        """evaluate a single item with possible offers"""
        partial = Decimal()
        offer = self.lookup_offer(item)
        remaining_quantity = quantity
        if offer:
            # add applied offers
            remaining_quantity = offer.residual(quantity)
            partial += offer.times(quantity) * offer.price

        partial += remaining_quantity * item.price
        return partial, offer

    def calculate(self, basket: Basket) -> Order:
        """calculate order"""
        order = Order()

        for item, quantity in basket.get_items().items():
            order.add_item(Item(item.name, item.price, quantity))
            order.partials[item], offer = self.evaluate_partial(item, quantity)
            if offer:
                order.include_offer(offer, offer.times(quantity))
            order.total += order.partials[item]

        return order
