#!bin/usr/env python3

# SQLite utilities for the Amazon Scraper

import sqlite3
import datetime


# This is a stupid thing to do.
# But I wanted to learn a bit more about decorators, and this code will never see the light of a production env.
# So this piece of code exists.
def sqliteException(function):
    def application(*args,**kwargs):
        try:
            return function(*args, **kwargs)
        except sqlite3.Error as e:
            print(function.__name__)
            print("An error occurred: ", e.args[0])
    return application

@sqliteException
def getConnection(dbName):
    """Creates and returns a connections to a SQLite DB.

    Arguments:
        dbName {string} -- Path for the database.

    Returns:
        SQLite Connection -- A SQLite connection to the db.
    """
    return sqlite3.connect(dbName)

@sqliteException
def createTable(connection):
    connection.cursor().execute('''CREATE TABLE IF NOT EXISTS products (id text, date date, countryCode text, currentPrice real, isDeal real, available real)''')
    connection.commit()

@sqliteException
def insert(data, connection):
    """Inserts data into a product table

    Arguments:
        id {string} -- The product ID, which is the name of the table.
        data {tuple} -- The data to be inserted. Must be in this format (id: string, data: datetime.datetime.now(), currentPrice: float, isDeal: 0 or 1, available: 0 or 1)
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute("INSERT INTO products VALUES (?,?,?,?,?,?)", data)
    connection.commit()

@sqliteException
def clearTable(connection):
    """Clears every record from the table.
        Vacuum is used to clear unused space.

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute("delete from products")
    connection.commit()
    connection.cursor().execute("vacuum")
    connection.commit()

@sqliteException
def dropTable(connection):
    connection.cursor().execute('drop table products')
    connection.commit()

@sqliteException
def selectWithID(id, connection):
    """Selects all entries on the database where the ID matches with the given ID.

    Arguments:
        id {string} -- The ID of the product
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        List -- A list of tuples. Each tuples is an entry in the database.
    """
    cursor = connection.cursor()
    return cursor.execute('select * from products where id = ?', (id,)).fetchall()

@sqliteException
def selectByAvailability(connection):
    """Selects all entries which are available today.

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        List -- A list of tuples. Each tuples is an entry in the database.
    """
    cursor = connection.cursor()
    return cursor.execute('select * from products where available = 1 and date = ?', (str(datetime.date.today()),)).fetchall()

@sqliteException
def selectByCurrentDeal(connection):
    """Selects all entries which have available deals today.

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        List -- A list of tuples. Each tuples is an entry in the database.
    """
    cursor = connection.cursor()
    return cursor.execute('select * from products where isDeal = 1 and date = ?', (str(datetime.date.today()),)).fetchall()

@sqliteException
def getAllItems(connection):
    """Gets all the items that are being stored in the database

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        List -- A list of tuples. Each tuple is a distinct item id.
    """
    cursor = connection.cursor()
    return cursor.execute('select distinct id from products').fetchall()


@sqliteException
def getLastDate(connection):
    """Gets the date of the last insert.
    There should be a better way to do this...

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        datetime object -- the datetime object of the last date.
    """
    cursor = connection.cursor()
    return datetime.datetime.strptime(cursor.execute('SELECT MAX(date) from products').fetchone()[0], '%Y-%m-%d').date()

@sqliteException
def getTodaysValues(connection):
    """Gets entries from today.

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        List -- A list of tuples. Each tuple is an item that was scraped.
    """
    cursor = connection.cursor()
    return cursor.execute('SELECT * from products where date = ?', (datetime.date.today(),)).fetchall()


@sqliteException
def checkIfPriceDropped(id, connection):
    """Checks if the price dropped from yesterday to today.

    Arguments:
          Arguments:
        id {string} -- The product ID, which is the name of the table.
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        Boolean
    """

    cursor = connection.cursor()
    today = cursor.execute('SELECT currentPrice from products where id = ? and date = ?', (id, datetime.date.today())).fetchone()
    yesterday = cursor.execute('SELECT currentPrice from products where id = ? and date = ?', (id, datetime.date.today()- datetime.timedelta(days=1))).fetchone()
    if today < yesterday:
        return True
    return False

if __name__ == "__main__":
    c = getConnection('test.db')
    # clearTable(c)
    # dropTable(c)
    createTable(c)
    # print(getLastDate(c))
    # data = ["asdasafasd", datetime.date.today(), float(90.9), 1, 1]
    # insert(data, c)
    # data = ["rrrrrr", datetime.date.today(), float(91.9), 1, 1]
    # insert(data, c)

    # available = selectByAvailability(c)
    # print(available)

    # deal = selectByCurrentDeal(c)
    # print(deal)
    c.close()