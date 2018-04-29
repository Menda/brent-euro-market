from datetime import datetime
import os
from unittest import TestCase

from ..producers import (binary_search_csv, price_generator, _get_tendency,
                         _get_linear_progress)


class BinarySearchCSVTest(TestCase):
    def setUp(self):
        self.filename = os.path.join('simulators', 'data', 'Brent_USD.csv')

    def test_binary_search_csv_exact(self):
        target = datetime(2012, 12, 1)
        result = binary_search_csv(self.filename, target)
        self.assertEqual(result[0], ['2012-12-01', '109.64'])

    def test_binary_search_csv_exact_first_value(self):
        target = datetime(2007, 6, 1)
        result = binary_search_csv(self.filename, target)
        self.assertEqual(result[0], ['2007-06-01', '71.32'])

    def test_binary_search_csv_exact_first_value_extra_results_2(self):
        target = datetime(2007, 6, 1)
        result = binary_search_csv(self.filename, target, 2)
        self.assertEqual(result[0], ['2007-06-01', '71.32'])
        self.assertEqual(result[1], ['2007-07-01', '77.2'])
        self.assertEqual(result[2], ['2007-08-01', '70.8'])

    def test_binary_search_csv_exact_last_value(self):
        target = datetime(2017, 6, 1)
        result = binary_search_csv(self.filename, target)
        self.assertEqual(result, [['2017-06-01', '46.8945454545455']])

    def test_binary_search_csv_exact_last_value_extra_results_0(self):
        target = datetime(2017, 6, 1)
        result = binary_search_csv(self.filename, target, 0)
        self.assertEqual(result, [['2017-06-01', '46.8945454545455']])

    def test_binary_search_csv_exact_last_value_extra_results_5(self):
        target = datetime(2017, 6, 1)
        result = binary_search_csv(self.filename, target, 5)
        self.assertEqual(result, [['2017-06-01', '46.8945454545455']])


class GetTendencyTest(TestCase):
    def test_get_tendency_positive(self):
        self.assertEqual(_get_tendency(0.03, 97, 100), 1)

    def test_get_tendency_positive_big(self):
        self.assertEqual(_get_tendency(0.03, 100, 200), 1)

    def test_get_tendency_negative(self):
        self.assertEqual(_get_tendency(0.03, 100, 97), -1)

    def test_get_tendency_negative_big(self):
        self.assertEqual(_get_tendency(0.03, 100, 50), -1)

    def test_get_tendency_unknown_decrease(self):
        self.assertEqual(_get_tendency(0.03, 100, 98), None)

    def test_get_tendency_unknown_increase(self):
        self.assertEqual(_get_tendency(0.03, 98, 100), None)


class GetLinearProgressTest(TestCase):
    def test_get_linear_progress(self):
        prices = _get_linear_progress(100, 120, 5)
        self.assertEqual(len(prices), 5)


class PriceGeneratorTest(TestCase):
    def _check_percental_max(self, prices, change_percental_max):
        initial_price = prices[0]
        for price in prices:
            self.assertLess(abs(price / initial_price - 1) / 100,
                            change_percental_max)

    def test_price_generator_invalid_change_percental_max(self):
        self.assertRaises(ValueError, price_generator, 100, 10, 100, 120)

    def test_price_generator_huge_positive_change(self):
        change_percental_max = 30
        prices = price_generator(100, change_percental_max, 100, 120)
        self.assertEqual(len(prices), 100)
        self.assertEqual(prices[-1], 120)
        self._check_percental_max(prices, change_percental_max)
        print("")
        print(prices)

    def test_price_generator_huge_negative_change(self):
        change_percental_max = 30
        prices = price_generator(100, change_percental_max, 125, 100)
        self.assertEqual(len(prices), 100)
        self.assertEqual(prices[-1], 100)
        self._check_percental_max(prices, change_percental_max)

    def test_price_generator_negative_change(self):
        change_percental_max = 30
        prices = price_generator(100, change_percental_max, 110, 100)
        self.assertEqual(len(prices), 100)
        self.assertEqual(prices[-1], 100)
        self._check_percental_max(prices, change_percental_max)
