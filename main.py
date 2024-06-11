import logging
from datetime import datetime, timedelta
from aiohttp import ClientSession, ClientConnectorError
import pprint
import sys
import asyncio

URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

async def dates_list(days_numb=None):
    dates = []
    current_date = datetime.now()
    dates.append(URL + str(await date_formatting(current_date)))
    if days_numb:
        for i in range(1, days_numb):
            delta = timedelta(days=i)
            dates.append(URL + str(await date_formatting(current_date - delta)))
    return dates

async def date_formatting(date):
    return date.strftime("%d.%m.%Y")

async def get_exchange(days_numb=None):
    if days_numb is not None and days_numb > 10:
        return '10 days is max('
    urls = await dates_list(days_numb)
    json_result = [await request(url) for url in urls]
    result_list = []
    if json_result:
        for dictionary in json_result:
            exchange_date = dictionary['date']
            exchange_data = {exchange_date: {}}
            for inner_dictionary in dictionary['exchangeRate']:
                if inner_dictionary['currency'] == 'EUR':
                    eur_data = {'EUR': {'sale': inner_dictionary['saleRate'],
                                        'purchase': inner_dictionary['purchaseRate']}}
                    exchange_data[exchange_date].update(eur_data)
                elif inner_dictionary['currency'] == 'USD':
                    usd_data = {'USD': {'sale': inner_dictionary['saleRate'],
                                        'purchase': inner_dictionary['purchaseRate']}}
                    exchange_data[exchange_date].update(usd_data)
            result_list.append(exchange_data)
        return result_list
    else:
        return "Data retrieval failed("
      
async def request(url: str):
    async with ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.ok:
                    r = await response.json()
                    return r
                logging.error(f'Error status: {response.status} for {url}')
                return None
        except ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None

if __name__ == "__main__":
    if len(sys.argv) == 2:
        days_numb = int(sys.argv[1])
    else:
        days_numb = None
    result = asyncio.run(get_exchange(days_numb))
    pprint.pprint(result)
