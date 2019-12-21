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
import matplotlib.pyplot as plt

DBNAME = ''

def showDailyPrices(connection):
    """Shows the daily prices for every item in the database

    Arguments:
        connection {SQLiteObject} -- A connection ot the database.
    """
    return getTodaysValues(connection)

def newProduct(id, connection):
    """Inserts a new product in the database.
    Searchs all of the  Amazon websites for values and inserts them in the database.

    Arguments:
        id {string} -- ID of the product.
        connection {SQLiteObject} -- A connection ot the database.

    """

    print("*** Inserting new product with id {} ***".format(id))
    for k,v in COUNTRY.items():
        a = getProductPrice(k, id)
        if not a:
            print("*** Product does not exists in {} ***".format(v['code']))
        else:
            print('ID: {} | Price: {} | Is Deal?: {} | Is Available?: {} | Country: {}'.format(a[0], a[3], a[4], a[5], a[2]))
            insertToDatabase(a, connection)
        time.sleep(5)

def getDeals(connection):
    """Gets the available deals today.

    Arguments:
        connection {SQLiteObject} -- A connection ot the database.

    """
    return selectByCurrentDeal(conn)

def showAllIds(connection):
    return [x[0] for x in getAllItems(connection)]

def pricePriceHistory(id, connection):
    """Gets the full price history from a product.
    TODO Add a date range.

    Arguments:
        id {string} -- ID of the product.
        connection {SQLiteObject} -- A connection ot the database.

    """
    # Creates a tuple where the first value is the country, and the second the date, and the third the value.
    return [(x[2], x[1], x[3]) for x in selectWithID(id, conn)]

def showPriceGraph(id, connection, **kwargs):
    """Show the graph for a certain item.

    Arguments:
        id {string} -- ID of the product.
        connection {SQLiteObject} -- A connection ot the database.

    """
    d = {}
    ticks = []
    for i in pricePriceHistory(id, connection):
        if i[0] not in d.keys():
            if 'selectedCountries' in kwargs.keys() and i[0] in kwargs['selectedCountries'] or 'selectedCountries' not in kwargs.keys():
                d[i[0]] = [[i[2]], [i[1]]]
        else:
            d[i[0]][0].append(i[2])
            d[i[0]][1].append(i[1])

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for k,v in d.items():
        ax1.plot(v[0], label=k)
        # Checks if the country has a larger history than the previous
        # This is needed because there are some items that become unavailable in certain countries.
        if len(v[1]) > len(ticks):
            ticks = v[1]

    ax1.set_xticklabels(ticks)
    ax1.legend()
    # Setting rotation of xticks
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    # Spacing between xticks and bottom.
    plt.subplots_adjust(bottom=0.20)
    plt.show()

if __name__ == "__main__":
    conn = getConnection('test.db')
    print(getDeals(conn))
    # showPriceGraph('B07XPPN1DS', conn)