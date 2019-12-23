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
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

AMAZON = "https://amazon.{}/dp/{}"

COUNTRY = {
    'fr': {'code': "FRANCE", 'currency': 'EUR'},
    'it': {'code': "ITALY", 'currency': 'EUR'},
    'co.uk': {'code': "UK", 'currency': 'GBP'},
    'es': {'code': "SPAIN", 'currency': 'EUR'},
    'com': {'code': "US", 'currency': 'USD'},
    'de': {'code': "GERMANY", 'currency': 'EUR'}
}

# DECORATOR FOR LOGGING
def log(function):
    def wrapper(*args, **kwargs):
        logging.debug('Starting {}'.format(function.__name__))
        values = function(*args, **kwargs)
        if values:
            logging.info('ID: {} | Price: {} | Is Deal?: {} | Is Available?: {} | Country: {}'.format(values[0], values[3], values[4], values[5], values[2]))
        else:
            logging.info("*** Not Available ***")
        return values
    return wrapper

@log
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

    if isLocal:
        soup = BeautifulSoup(open(isLocal, "r").read(), "html.parser") # Creates a BS object from a local HTML file
    else:
        print(AMAZON.format(countryCode, productId))
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.get(AMAZON.format(countryCode, productId))

    if save:
        # If we want to save the page, pass it a path, terminating with .html
        with open(save, "w") as f: f.write(soup.prettify())

    # Okay... So.
    # Selenium does not return None when it doesn't find a id. It throws an exception.
    # Because this is not a problem for us, we go around it.
    try:
        price = driver.find_element_by_id("priceblock_ourprice").text
    except:
        price = None
    try:
        dealprice = driver.find_element_by_id("priceblock_dealprice").text
    except:
        dealprice = None
    driver.quit()

    deal = False
    available = True
    if dealprice:
        deal = True
        currentPrice = float(dealprice.strip().split()[0].replace(",", ".").replace('£', ''))
        # Strips all the spaces and special characters from the price, and turns it into a float.
    elif not dealprice and not price:
        available = False
        currentPrice = 0
        return False
    else:
        currentPrice = float(price.strip().split()[0].replace(",", ".").replace('£', ''))

    if COUNTRY[countryCode]['currency'] != 'EUR': # I only care about the price in Euros. As such I convert automatically.
        currentPrice = moneyConversion(currentPrice, COUNTRY[countryCode]['currency'])

    return (productId, datetime.date.today(), COUNTRY[countryCode]['code'], currentPrice, deal, available)


def insertToDatabase(data, connection):
    """Inserts data into the database

    Arguments:
        data {Tuple} -- A tuple with the specifications of the table entry.
        connection {SQLiteObject} -- A connection ot the database.

    """
    insertProduct(data, connection)


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


def runner(database):
    """
    Searches all the selected Amazon stores for the products in the database, and inserts the new values in the database.

    Arguments:
        connection {SQLiteObject} -- A connection ot the database.
    """

    conn = getConnection(database)
    allItems = getAllItems(conn)
    print("* There are {} items *".format(len(allItems)))
    if len(allItems) > 0:
        for i in getAllItems(conn):
            print("** Starting product with ID: {} **".format(i[0]))
            for k,v in COUNTRY.items():
                print("*** Checking price for {} in {} ***".format(i[0], v['code']))
                a = getProductPrice(k, i[0])
                if a:
                    print('ID: {} | Price: {} | Is Deal?: {} | Is Available?: {} | Country: {}'.format(a[0], a[3], a[4], a[5], a[2]))
                    insertToDatabase(a, conn)
                else:
                    print("*** Product Not Available ***")
                time.sleep(5)
    print("*** Scraping Finished for Today: {} ! Come back tomorrow! ***".format(datetime.date.today()))
    logging.info("*** Scraping Finished for Today: {} ! Come back tomorrow! ***".format(datetime.date.today()))

if __name__ == "__main__":
    logging.basicConfig(filename='/home/quietswami/scraper.log', level=logging.INFO)