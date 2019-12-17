#!bin/usr/env python3

# Scraps Amazon for the price of a given product.

import requests
from bs4 import BeautifulSoup
import datetime
import sys
from dbutils import *
import json
import time
import logging

AMAZON = "https://amazon.{}/dp/{}"

DBNAME = ""

COUNTRY = {
    'fr': {'code': "FRANCE", 'currency': 'EUR'},
    'it': {'code': "ITALY", 'currency': 'EUR'},
    'co.uk': {'code': "UK", 'currency': 'GBP'},
    'es': {'code': "SPAIN", 'currency': 'EUR'},
    'com': {'code': "US", 'currency': 'USD'},
    'de': {'code': "GERMANY", 'currency': 'EUR'}
}

# DECORATOR FOR LOGGING
# TODO Finish it...
def log(function):
    def wrapper(*args, **kwargs):
        logging.debug('Starting {}'.format(function.__name__))
        return function(*args, **kwargs)
    return wrapper

def getProductPrice(countryCode, productId, isLocal=None, save=None):
    """Returns the Amazon page for a specific product as an BS object.

    Arguments:
        countryCode {str} -- The website country code for the Amazon Web site.
        productId {str} -- The id for the product to be searched.
        isLocal {None} -- When using a local HTML file (recomended for testing), pass the file path to load the local HTML file.
        save {None} -- Stores the page as an HTML file. If a path is passed, it will store the page to the given path.
    Returns:
        Dict -- A dictionary with the date, current price, and if that price is a deal.
    """

    try:
        if isLocal:
            soup = BeautifulSoup(open(isLocal, "r").read(), "html.parser") # Creates a BS object from a local HTML file
        else:
            print(AMAZON.format(countryCode, productId))
            headers = { "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}
            r = requests.get(AMAZON.format(countryCode, productId), headers=headers) # Gets the web page
            soup = BeautifulSoup(r.content, "html.parser")

        if save:
            # If we want to save the page, pass it a path, terminating with .html
            with open(save, "w") as f: f.write(soup.prettify())

        price = soup.find(id="priceblock_ourprice")
        dealprice = soup.find(id="priceblock_dealprice")
        deal = False
        available = True
        if dealprice:
            deal = True
            currentPrice = float(dealprice.text.strip().split()[0].replace(",", "."))
            # Strips all the spaces and special characters from the price, and turns it into a float.
        elif not dealprice and not price:
            available = False
            currentPrice = 0
        else:
            currentPrice = float(price.text.strip().split()[0].replace(",", "."))

        if COUNTRY[countryCode]['currency'] != 'EUR': # I only care about the price in Euros. As such I convert automatically.
            currentPrice = moneyConversion(currentPrice, COUNTRY[countryCode]['currency'])

        return (productId, datetime.date.today(), COUNTRY[countryCode]['code'], currentPrice, deal, available)
    except:
        print("FAIL")


def insertToDatabase(data):
    """Inserts data into the database

    Arguments:
        data {Tuple} -- A tuple with the specifications of the table entry.
    """
    conn = getConnection()
    insertToDatabase(data, conn)


def moneyConversion(baseValue, baseCurrency):
    """Checks the Exchange Rates API for the most up to date values, and converts the value.

    Arguments:
        baseValue {float} -- The price of the item.
        baseCurrency {string} -- 3 letter code for the currency. Check COUNTRY dict.

    Returns:
        float -- The base value converted to Euros.
    """
    r = requests.get('https://api.exchangeratesapi.io/latest')
    rates = json.loads(r.text)['rates']
    return baseValue / rates[baseCurrency]


def runner():
    """Code that runs every x minutes/hours/days?
    Searchs all the selected amazon stores for the product, and inserts it in the database.
    """
    if lastDate < datetime.date.today():
        for i in getAllItems(getConnection(DBNAME)):
            print("*** Starting product with ID: {} ***".format(i))
            for k,v in COUNTRY:
                print("*** Checking price for {} in {} ***".format(i, v['code']))
                insertToDatabase(getProductPrice(k, i[0]))
                time.sleep(5)
    else:
        # Sleeping for one hour...
        # This function should really be on a cronjob, but for illustration purposes...
        time.sleep(3600)
        runner()

if __name__ == "__main__":
    runner()