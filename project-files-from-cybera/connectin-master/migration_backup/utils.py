import datetime
import json
import math
import pyodbc
import pandas as pd

def file_read(path: str):
    """ Read a file and return content. """
    try:
        handler = open(path, 'r')
        data = handler.read()
        handler.close()
        return data
    except Exception as e:
        print('Exception: %s' % str(e))
        return None


def file_write(path: str, mode: str, content: str):
    """ Write content to a file. """
    handler = open(path, mode)
    handler.write(content)
    handler.close()


def get_connection(driver:str,host: str, port: str, username: str, password: str, db: str):
    cnxn = pyodbc.connect(driver=driver, server=host,port=port, database=db, uid=username, pwd=password)

    return cnxn


def execute_sql(cnxn: object, sql: str):
    try:
        data = pd.read_sql(sql,cnxn)
    except Exception as e:
        print("MySQL error %s: %s" % (e.args[0], e.args[1]))
        data = None
    return data
