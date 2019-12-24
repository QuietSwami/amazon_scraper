#!bin/usr/env python3

# SQLite utilities for the Amazon Scraper

import sqlite3
import datetime

'''

'''

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

#region Creation

@sqliteException
def createProductTable(connection):
    """Creates the product table.

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute('''CREATE TABLE IF NOT EXISTS products (id text, date date, countryCode text, currentPrice real, isDeal real, available real)''')
    connection.commit()

@sqliteException
def createUserTable(connection):
    """Creates the user table.

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute('''CREATE TABLE IF NOT EXISTS user (ID INTEGER PRIMARY KEY AUTOINCREMENT, email text)''')
    connection.commit()


@sqliteException
def createSubscriptionTable(connection):
    """Creates the user table.

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute('''CREATE TABLE IF NOT EXISTS subscription (userId text, productId text)''')
    connection.commit()

#endregion

#region Insertion

@sqliteException
def insertProduct(data, connection):
    """Inserts data into a product table

    Arguments:
        data {tuple} -- The data to be inserted. Must be in this format (id: string, data: datetime.datetime.now(), currentPrice: float, isDeal: 0 or 1, available: 0 or 1)
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute("INSERT INTO products VALUES (?,?,?,?,?,?)", data)
    connection.commit()

@sqliteException
def insertUser(email, connection):
    """Inserts data into a product table

    Arguments:
        email {string} -- The email of the user.
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute("INSERT INTO user (email) VALUES (?)", email)
    connection.commit()

@sqliteException
def insertSubscription(data, connection):
    """Inserts data into a product table

    Arguments:
        data {tuple} -- The data to be inserted. Must be in this format (userId: string, productId: string)
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute("INSERT INTO subscription VALUES (?,?)", data)
    connection.commit()

#endregion

#region Delete/Drop

@sqliteException
def clearTable(table, connection):
    """Clears every record from the table.
        Vacuum is used to clear unused space.

    Arguments:
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute("delete from {}".format(table))
    connection.commit()
    connection.cursor().execute("vacuum")
    connection.commit()

@sqliteException
def dropTable(table, connection):
    """Drops the table.

    Arguments:
        table {string} -- The name of the table to be dropped
        connection {SQLiteConnection} -- A SQLite connection.
    """
    connection.cursor().execute('drop table {}'.format(table))
    connection.commit()

#endregion

#region Product Select

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
    return cursor.execute('select distinct id, currentPrice from products where isDeal = 1 and date = ?', (str(datetime.date.today()),)).fetchall()

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

@sqliteException
def getLastEntryByID(id, connection):
    """Returns the last entry for a specific ID.
    Currently, it gets when the entries for the current date.

    Arguments:
        id {string} -- The product ID, which is the name of the table.
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        Tuple -- The value of the last entry for the given ID.
    """

    cursor = connection.cursor()
    return cursor.execute('SELECT * from products where id = ? and date = ?', (id, datetime.date.today())).fetchall()

@sqliteException
def getEntryByDateCountry(id, country, date, connection):
    """Returns if there is an entry where the fields are the given ones.

    Arguments:
        id {string} -- The product ID, which is the name of the table.
        country {string} -- The country code.
        date {datetime.date} -- The desired serached date.
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        [type] -- [description]
    """
    cursor = connection.cursor()
    return cursor.execute('SELECT * from products where id = ? and countryCode = ? date = ?', (id, country, date)).fetchone()

@sqliteException
def doesUserExists(id, connection):
    """Returns 1 if user exists.

    Arguments:
        id {string} -- The requested user ID.
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        Boolean -- Returns True if there is a user with the ID = id.
    """
    cursor = connection.cursor()
    return bool(cursor.execute('SELECT CASE WHEN EXISTS (\
    SELECT *\
    FROM user\
    WHERE id = ?\
    )\
    THEN CAST(1 AS BIT)\
    ELSE CAST(0 AS BIT) END', (id,)).fetchone()[0])

@sqliteException
def doesProductExist(id, connection):
    """Returns 1 if user exists.

    Arguments:
        id {string} -- The requested product ID.
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        Boolean -- Returns True if there is a user with the ID = id.
    """
    cursor = connection.cursor()
    return bool(cursor.execute('SELECT CASE WHEN EXISTS (\
    SELECT *\
    FROM product\
    WHERE id = ?\
    )\
    THEN CAST(1 AS BIT)\
    ELSE CAST(0 AS BIT) END', (id,)).fetchone()[0])


@sqliteException
def getUserSubscriptions(id, connection):
    """Return a users subscriptions.

    Arguments:
        id {string} -- The user ID.
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        Boolean -- Returns True if there is a user with the ID = id.
    """
    cursor = connection.cursor()
    return cursor.execute('SELECT * from subscriptions where userID = ?', (id,)).fetchall()

@sqliteException
def isUserSubscribed(userID, productID, connection):
    """Checks if user is subscribed for a product, and returns its email.

    Arguments:
        userID {string} -- The user ID.
        productID {string} -- The product ID.
        connection {SQLiteConnection} -- A SQLite connection.

    Returns:
        Boolean -- Returns True if there is a user with the ID = id.
    """
    cursor = connection.cursor()
    return bool(cursor.execute('SELECT CASE WHEN EXISTS (\
    SELECT *\
    FROM subscription\
    WHERE userID = ?\
    and productID = ?\
    )\
    THEN CAST(1 AS BIT)\
    ELSE CAST(0 AS BIT) END', (userID, productID)).fetchone()[0])

def usersBySubscription(productID, connection):
    cursor = connection.cursor()
    return cursor.execute('select userID from subscription where productID = ?', (productID,)).fetchall()

def getEmail(userId, connection):
    cursor = connection.cursor()
    return cursor.execute('select email from user where id = ?', (userId,)).fetchone()

#endregion

if __name__ == "__main__":
    c = getConnection('test.db')
    # createSubscriptionTable(c)
    # createUserTable(c)
    # dropTable('user', c)
    createUserTable(c)
    insertUser(('fran.abm94@gmail.com',),c)
    # clearTable(c)
    # dropTable(c)
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
