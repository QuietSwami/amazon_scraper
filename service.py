#!bin/usr/env python3

# Runs on a server and combines all of the services provided by the bot - except the viewer.
from scraper import *

from dbutils import *
from emailUtils import *
import logging
import datetime

def productScrap(productID, connection):
    for k,v in COUNTRY.items():
        print("*** Checking price for {} in {} ***".format(i[0], v['code']))
        a = getProductPrice(k, i[0])
        if a:
            print('ID: {} | Price: {} | Is Deal?: {} | Is Available?: {} | Country: {}'.format(a[0], a[3], a[4], a[5], a[2]))
            insertToDatabase(a, connection)
            if a[4]:
                sendDeal()
        else:
            print("*** Product Not Available ***")

def checkPriceChange(id, country, date, currentPrice, conn):
    price = getEntryByDateCountry(id, country, date, conn)[3]
    if price > currentPrice:
        return True
    return False

def registerNewUser(email, conn):
    insertUser(email)

def registerNewSubscription(userID, productID, conn):
    if doesUserExists(userID, conn):
        if doesProductExist(productID, conn):
            insertSubscription((userID, productID))
        else:
            logging.info('*** Product with ID: {} is not on the database. Starting Scrape... ***'.format(productID))


def run(database):
    conn = getConnection(database)
    allItems = getAllItems(conn)
    logging.info("* There are {} items *".format(len(allItems)))
    if len(allItems) > 0:
        for i in getAllItems(conn):
            print("** Starting product with ID: {} **".format(i[0]))
            for k,v in COUNTRY.items():
                print("*** Checking price for {} in {} ***".format(i[0], v['code']))
                a = getProductPrice(k, i[0])
                if a:
                    print('ID: {} | Price: {} | Is Deal?: {} | Is Available?: {} | Country: {}'.format(a[0], a[3], a[4], a[5], a[2]))
                    insertToDatabase(a, conn)
                    if a[4]:
                        sendPriceDrop()
                    elif checkPriceChange(a[0], a[2], datetime.date.today() - datetime.timedelta(days=1),  a[3]):
                        sendDeal()
                else:
                    print("*** Product Not Available ***")
                time.sleep(5)

    print("*** Scraping Finished for Today: {} ! Come back tomorrow! ***".format(datetime.date.today()))
    logging.info("*** Scraping Finished for Today: {} ! Come back tomorrow! ***".format(datetime.date.today()))

if __name__ == '__main__':
    logging.basicConfig(filename='/home/quietswami/scraper.log', level=logging.INFO)

