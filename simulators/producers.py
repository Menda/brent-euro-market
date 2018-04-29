import asyncio
import csv
from datetime import datetime
import random
from typing import List, Tuple, Optional

DateValue = Tuple[str, str]

TENDENCY_THRESHOLD = 0.03
SPREAD_POINTS = 5
VOLATILITY = {
    'really_low': 0.01,
    'low': 0.025,
    'medium': 0.05,
    'medium_high': 0.07,
    'high': 0.1,
}


def binary_search_csv(filename: str, target: datetime,
                      extra_results: int = None) -> List[DateValue]:
    """
    There are two ways to implement it:

    * The file size is small (this case): load all data into memory and then
      operate just in memory. It is really fast.
    * The file size is huge: if we don't have enough memory to allocate the
      whole file, we need to use iterators, as they just store in memory the
      current line processed. When finishes it gets garbage collected. It is
      slow, as we will need to jump inside the file (IO file seek) several
      times when doing the binary search.
    """
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip the headers
        rows = list(reader)

        start = 0
        end = len(rows)
        while True:
            if end - start == 0:
                break

            middle = (end + start) // 2
            date_str = rows[middle][0]
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            if dt == target:
                if not extra_results:
                    return rows[middle:]
                else:
                    until = middle + extra_results
                    if until > (len(rows) - 1):
                        until = (len(rows) - 1)
                    return rows[middle:until + 1]
            elif dt < target:
                start = middle
            elif dt > target:
                end = middle


def _get_tendency(threshold: float, start_price: float, end_price: float) -> \
        Optional[int]:
    """
    If the difference of the start price and the end price is big, then this
    defines the tendency (+1) for the whole day. The same if it's negative
    (-1). If there is not a strong one, then returns None.
    """
    if end_price < start_price:
        difference = (end_price / start_price) * -1
    else:
        difference = start_price / end_price
    if abs(abs(difference) - 1) >= threshold:
        if difference < 0:
            tendency = -1
        else:
            tendency = 1
    else:
        tendency = None
    return tendency


def _get_volatility(tendency: Optional[int]) -> float:
    """
    If the difference is positive then by general rule volatility is low. If
    the difference is negative, the volatility is high.
    """
    if tendency >= 0:
        return VOLATILITY[random.choice(['really_low', 'low'])]
    elif tendency < 0:
        return VOLATILITY[random.choice(['low', 'medium'])]
    else:
        return VOLATILITY['really_low']


def _get_linear_progress(start_price: float, end_price: float,
                         num_points: int) -> list:
    """
    Given we have a start and endpoints and a number of intermediate points to
    paint, instead of making them in a linear way, make them look random.
    """
    prices = [start_price]
    objective = start_price
    step = (end_price - start_price) / (num_points - 1)

    repeated = 0
    for i in range(num_points - 2):
        objective += step
        if repeated:
            if pos_neg:
                weight_pos = 0.5 / ((repeated + 1) * 0.5)
                weight_neg = 1 - weight_pos
            else:
                weight_neg = 0.5 / ((repeated + 1) * 0.5)
                weight_pos = 1 - weight_neg
            pos_neg_n = random.choices(
                [-1, 1], weights=[weight_neg, weight_pos])
            if pos_neg == pos_neg_n:
                repeated += 1
            else:
                repeated = 0
        else:
            pos_neg = random.choice([-1, 1])
            if pos_neg < 0:
                pos_neg = 1
            else:
                pos_neg = -1
        price_noisy = objective + step * random.random() * pos_neg * 2
        prices.append(price_noisy)

    prices.append(end_price)
    return prices


def price_generator(num_points: int, change_percental_max: float,
                    start_price: float, end_price: float):

    prices = [start_price]
    last_price = start_price

    if change_percental_max < abs((end_price / start_price - 1) * 100):
        raise ValueError()

    tendency = _get_tendency(TENDENCY_THRESHOLD, start_price, end_price)
    volatility = _get_volatility(tendency)

    # Since when we start approaching the target end price
    range_high = max(1, int(num_points * 0.2))
    if range_high >= 3:
        points_approach = random.randint(range_high-3, range_high)
    else:
        points_approach = random.randint(1, range_high)
    start_approach = num_points - points_approach

    for i in range(1, num_points - 1):
        if i >= start_approach:
            points = _get_linear_progress(
                last_price, end_price, num_points - i)
            prices += points
            break
        else:
            price_diff = (last_price/start_price) - 1
            current_percental = abs(price_diff) * 100
            if current_percental >= change_percental_max:
                if price_diff > 0:
                    change_percent -= (2 * volatility)
                elif price_diff <= 0:
                    change_percent += (2 * volatility)
            else:
                if tendency >= 0 and last_price < end_price:
                    factor = 1.5
                elif tendency < 0 and last_price > end_price:
                    factor = 2.5
                else:
                    factor = 2
                change_percent = factor * volatility * random.random()
                if change_percent > volatility:
                    change_percent -= (2 * volatility)

            change_amount = last_price * change_percent
            new_price = last_price + change_amount

        prices.append(new_price)
        last_price = new_price
    else:
        # Aproach 100%
        prices.append(end_price)

    return prices


async def producer(name: str):
    print('Running producer: {}'.format(name))
    while True:
        await asyncio.sleep(5)
        binary_search_csv('simulators/data/Brent_USD.csv')


def main():
    ioloop = asyncio.get_event_loop()
    tasks = [
        ioloop.create_task(producer('usd-eur')),
    ]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()


if __name__ == "__main__":
    main()
