import _mysql_exceptions

__author__ = 'root'

from Exception import *

class BaseSQLManager(object):

    conn = None
    cursor = None

    def __init__(self, host='localhost', port=3306, user='root', passwd='root',db=None):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        if not db:
            raise DBNotExistException()
        self.db = db
        self.setup_connection()

    def setup_connection(self):
        try:
            import MySQLdb
        except ImportError,i:
            print(i)
            exit()
        else:
            try:
                self.conn = MySQLdb.connect(
                    host = self.host,
                    port = self.port,
                    user = self.user,
                    passwd = self.passwd,
                    db = self.db
                )
            except _mysql_exceptions.OperationalError, o:
                print(o)
                exit()

    def start_sql_connection(self):
        self.execute()
        self.close_db_connection()

    def close_db_connection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def execute(self):
        self.cursor = self.conn.cursor()
        self.do_execute()
        self.cursor.close()

    def do_execute(self):
        self.cursor.execute("insert into django_test_books value('fff33')")

if __name__ == '__main__':
    sql = BaseSQLManager(db='test_db')
    sql.start_sql_connection()
