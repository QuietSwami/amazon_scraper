#!bin/usr/env python3

# Viewer for the results of the Scrapers.
# Will temporarly have the some of the command line functions.

import requests
import datetime
import sys
from dbutils import *
from scraper import *
import json
import time
import matplotlib


DBNAME = ''

def showDailyPrices(database):
    """Shows the daily prices for every item in the database

    Arguments:
        database {string} -- The path to the .db file.
    """
    conn = getConnection(database)
    daily = getTodaysValues(conn)
    for i in daily:
        print('ID: {} | Price: {} | Is Deal?: {} | Is Available?: {} | Country: {}'.format(i[0], i[3], i[4], i[5], i[2]))

def newProduct(database, id):
    """Inserts a new product in the database.
    Searchs all of the  Amazon websites for values and inserts them in the databse.

    Arguments:
        database {string} -- The path to the .db file.
        id {string} -- ID of the product.
    """

    print("*** Inserting new product with id {} ***".format(id))
    for k,v in COUNTRY.items():
        a = getProductPrice(k, id, save="test-{}.html".format(k))
        if not a:
            print("*** Product does not exists in {} ***".format(v['code']))
        else:
            print('ID: {} | Price: {} | Is Deal?: {} | Is Available?: {} | Country: {}'.format(a[0], a[3], a[4], a[5], a[2]))
            insertToDatabase(a, database)
        time.sleep(5)

def getDeals(database):
    """Gets the available deals today.

    Arguments:
        database {string} -- [description]
    """
    conn = getConnection(database)
    deals = selectByCurrentDeal(conn)
    for i in deals:
        print('ID: {} | Price: {} | Is Deal?: {} | Is Available?: {} | Country: {}'.format(i[0], i[3], i[4], i[5], i[2]))


def showPriceHistory(database, id):
    """Gets the full price history from a product.
    TODO Add a time range.

    Arguments:
        database {string} -- [description]
    """
    conn = getConnection(database)
    history = [(x[1],x[3]) for x in selectWithID(id, conn)] # Creates a tuple where the first value is the date, and the second the price.
    print(history)

if __name__ == "__main__":
    newProduct('test.db', 'B07GDR2LYK')