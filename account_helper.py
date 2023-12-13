################################################################################
################################################################################
# You should NOT change anything here!
################################################################################
################################################################################
import psycopg2
import bcrypt
import requests


################################################################################
# PSQL                                                                                                                                                 #
################################################################################
psql_user = "pscefuxk"
psql_pw = "vuVfRfHNHLKv6d8EOWmf122LSySMgmS0"
psql_host = "flora.db.elephantsql.com"
psql_port = 5432
psql_database = "pscefuxk"

def get_psql_connection():
    """
    Input: None
    Connects to the psql database.
    Output: Connection to the psql database
    """
    return psycopg2.connect(
        user = psql_user,
        password = psql_pw,
        host = psql_host,
        port = psql_port,
        database = psql_database
    )

def query(cmd):
    """
    Input: Query we want to send to psql
    Calls _query with an argument to fetch something.
    Output: _query
    """
    return _query(cmd, True)

def query_no_fetch(cmd):
    """
    Input: Query we want to send to psql
    Calls _query with an argument to not fetch anything.
    Output: _query
    """
    _query(cmd, False)

def _query(cmd, fetch):
    """
    Input: Query we want to send to psql, Boolean
    Connects to a psql database and execute the given query. Depending
    on the boolean it then fetches a return or not before closing the connection.
    Output: what we fetched OR None
    """
    connection = get_psql_connection()
    cursor = connection.cursor()
    cursor.execute(cmd)
    connection.commit()
    if fetch:
        res = cursor.fetchall()
        cursor.close()
        connection.close()
        return res
    cursor.close()
    connection.close()
    return

def make_safe(s):
    """
    Input: String
    Makes a string safe by ensuring that it is not empty and replacing ' with "
    so that the string formatting we used for the sql queries works.
    Output: Safe String
    """
    if s == None:
        return "null"
    return s.replace("'", "''")


################################################################################
# Users                                                                                                                                                  #
################################################################################
def register_user(uname, psword):
    """
    Input: Strings (Username, Password)
    Checks whether a username already exists and if the user filled out all fields.
    Then it hashes the password and stores all the data in the psql table 'users'
    Output: String that indicates the success of this function
    """
    #checks if all boxes were filled out
    if uname == "" or psword == "":
        return "fill_out_all"
    #counts the given username, returns false if it counted >0
    res = query("SELECT COUNT(*) FROM users WHERE username='{}'".format(make_safe(uname)))
    if res[0][0] > 0:
        return "already_exists", uname
    #hashes the password so it is not clear in our database
    hashed_password = bcrypt.hashpw(psword.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    #inserts the new user into the table
    query_no_fetch("INSERT INTO users VALUES (DEFAULT, '{}', '{}')".format(make_safe(uname), make_safe(hashed_password)))
    return "user_registered", uname

def is_login_successful(uname, psword):
    """
    Input: Strings(Username, Password)
    Checks if the given password matches the password in the table.
    Output: String that indicates the success of this function
    """
    #checks if all boxes were filled out
    if uname == "" or psword == "":
        return "fill_out_all"
    #query to get the data corresponding to the given username
    res = query("SELECT * FROM users WHERE username='{}'".format(make_safe(uname)))
    #if the username doesn't exist
    if len(res) == 0:
        return "username_not_found", uname
    #if the correct password was entered
    if bcrypt.checkpw(psword.encode('utf-8'), res[0][2].encode('utf-8')):
        return "correct_password", uname
    #if none of the above worked
    return "wrong_password", uname


################################################################################
# Add, delete & query all                                                                                                                     #
################################################################################
def query_all_table(uname):
    """
    Input: Username
    Output: List with all items in the storage, Dictionary with a mapping
    for the id of the item
    """
    storage = query("SELECT * FROM storage WHERE username='{}'".format(make_safe(uname)))
    items = []
    mapping = {}
    for index, item in enumerate(storage):
        mapping[index+1] = item[0]
        items.append(item)
    return items, mapping

def query_delete(ind):
    """
    Input: Id of the Item to delete
    Deletes the Item with the given id.
    Output: None
    """
    query_no_fetch("DELETE FROM storage WHERE id='{}'".format(ind))

def query_add(uname, item_name):
    """
    Input: Strings (Username, Itemname)
    Adds an item to the database for this user.
    Output: None
    """
    query_no_fetch("INSERT INTO storage VALUES (DEFAULT, '{}', '{}')".format(make_safe(uname),
                                                                                                                                       make_safe(item_name)))
