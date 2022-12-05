import unittest

from katacheckout2 import Item, Basket, Order, CheckOut, SpecialOffer


class CheckoutTestCase(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_one_a_cost_30(self):
        basket = Basket()
        basket.add(Item("A", 30.0, 1))

        checkout = CheckOut()

        result = checkout.calculate(basket)

        self.assertEqual(result.total, 30)

    def test_add_item_in_basket(self):
        basket = Basket()
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("A", 50.0, 1))

        checkout = CheckOut()

        result = checkout.calculate(basket)

        self.assertEqual(result.total, 100)

    def test_two_items_in_basket(self):
        basket = Basket()
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("B", 30.0, 1))

        checkout = CheckOut()

        result = checkout.calculate(basket)

        self.assertEqual(result.total, 80)

    def test_three_items_in_basket(self):
        basket = Basket()
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("B", 30.0, 1))
        basket.add(Item("C", 10.0, 1))

        checkout = CheckOut()

        result = checkout.calculate(basket)

        self.assertEqual(result.total, 90)

    def test_multi_item_in_the_basket(self):
        basket = Basket()
        basket.add(Item("A", 50.0, 2))
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("B", 30.0, 1))
        basket.add(Item("C", 10.0, 1))

        checkout = CheckOut()

        result = checkout.calculate(basket)

        self.assertEqual(result.total, 190)
        self.assertEqual(result.get_partials("A"), 150)
        self.assertEqual(result.get_partials("B"), 30)
        self.assertEqual(result.get_partials("C"), 10)

    def test_special_offer(self):
        basket = Basket()
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("B", 30.0, 1))
        basket.add(Item("C", 10.0, 1))

        checkout = CheckOut()

        checkout.register_offer(SpecialOffer("A", 80, 2))

        result = checkout.calculate(basket)

        self.assertEqual(result.total, 170)
        self.assertEqual(result.get_partials("A"), 130)
        self.assertEqual(result.get_partials("B"), 30)
        self.assertEqual(result.get_partials("C"), 10)

    def test_multiple_special_offer(self):
        basket = Basket()
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("B", 30.0, 1))
        basket.add(Item("B", 30.0, 1))

        checkout = CheckOut()

        checkout.register_offer(SpecialOffer("A", 30, 2))
        checkout.register_offer(SpecialOffer("B", 30, 2))

        result = checkout.calculate(basket)

        self.assertEqual(result.total, 110)
        self.assertEqual(result.get_partials("A"), 80)
        self.assertEqual(result.get_partials("B"), 30)


class TestSpecialOffer(unittest.TestCase):
    def test_special_offer_residuals_correct(self):

        offer = SpecialOffer("A", 10.0, 2, "offer1")

        self.assertEqual(offer.residual(10), 0)
        self.assertEqual(offer.residual(3), 1)
        self.assertEqual(offer.residual(0), 0)

    def test_special_offer_times(self):
        offer = SpecialOffer("A", 10.0, 2, "offer1")

        self.assertEqual(offer.times(10), 5)
        self.assertEqual(offer.times(3), 1)
        self.assertEqual(offer.times(0), 0)

    def test_special_offer_price(self):
        offer = SpecialOffer("A", 10.0, 2, "offer1")

        self.assertEqual(offer.evaluate_price(10), 50)
        self.assertEqual(offer.evaluate_price(3), 10)
        self.assertEqual(offer.evaluate_price(0), 0)


class TestOrder(unittest.TestCase):
    def test_offer_applied(self):
        basket = Basket()
        basket.add(Item("A", 50.0, 2))
        basket.add(Item("A", 50.0, 1))
        basket.add(Item("B", 30.0, 1))
        basket.add(Item("C", 10.0, 1))

        checkout = CheckOut()

        offer = SpecialOffer("A", 80, 2)
        offer2 = SpecialOffer("D", 10, 3)
        checkout.register_offer(offer)
        checkout.register_offer(offer2)

        order = checkout.calculate(basket)

        self.assertEqual(order.total, 170)

        self.assertIn(offer, [a for a, _ in order.offers_applied])
        for _, quantity in order.offers_applied:
            self.assertEqual(quantity, 1)

        self.assertNotIn(offer2, [a for a, _ in order.offers_applied])
