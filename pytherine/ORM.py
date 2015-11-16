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

    def do_sql_connection(self, sql):
        self.execute(sql)
        self.close_db_connection()

    def do_sql_get_connection(self, sql):
        list = self.get_execute(sql)
        self.close_db_connection()
        return list

    def get_execute(self, sql):
        self.cursor = self.conn.cursor()
        num = self.cursor.execute(sql)
        info = self.cursor.fetchmany(num)
        result = []
        for i in info:
            result.append(i)
        self.cursor.close()
        return result

    def close_db_connection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def execute(self, sql):
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql)
        self.cursor.close()


def as_create_sql(name, maps):
    create_sql = []
    for k,v in maps.items():
        create_sql.append(k+' '+v.type)
    head = 'create table %s (%s)' % (name, ','.join(create_sql)) # create table table_name(name varchar(20))
    return head

def as_insert_sql(name, maps):
    insert_col_sql = []
    insert_value_sql = []
    for k,v in maps.items():
        insert_col_sql.append(v.col_name)
        insert_value_sql.append('\''+v.value+'\'')
    head = 'insert into %s(%s) value(%s)' % (name, ','.join(insert_col_sql), ','.join(insert_value_sql)) # insert into table_name value('233')
    return head

def as_get_sql(name, keys=None):
    if keys:
        where = []
        for k,v in keys.items():
            where.append(k+'=\''+v+'\'')
        return 'select * from %s where %s' % (name, ','.join(where))
    else:
        return 'select * from %s' % name


class Field(object):
    def __init__(self, col_name, type, value):
        self.col_name = col_name
        self.type = type
        self.value = value

class CharField(Field):
    def __init__(self, col_name):
        super(CharField, self).__init__(col_name, 'varchar(20)', None)


class ModelMetaclass(type):
    def __new__(cls, *args, **kwargs):
        if args[0] == 'Model':
            return type.__new__(cls, *args)
        attrs = args[-1]
        maps = {}
        for k,v in attrs.items():
            if isinstance(v, Field):
                maps[k] = v
        args[-1]['table_name'] = args[0]
        args[-1]['maps'] = maps
        return type.__new__(cls, *args)

conn = BaseSQLManager(db='test_db')

class Model(object):
    __metaclass__ = ModelMetaclass

    def __init__(self, **values):
        if values:
            for k,v in self.maps.items():
                if isinstance(v, Field):
                    v.value = values[k]

    def save(self):
        conn.do_sql_connection(as_insert_sql(self.table_name, self.maps))

    def create(self):
        conn.do_sql_connection(as_create_sql(self.table_name, self.maps))

    def get(self, **keys):
        get_result = conn.do_sql_get_connection(as_get_sql(self.table_name, keys))
        objs_list = []
        cols = []
        for k,v in self.maps.items():
            cols.append(k)
        for i in range(len(get_result)):
            obj = eval(self.__class__.__name__+'()')
            for j in range(len(cols)):
                # obj[cols[j]] = get_result[i][j]
                obj.__setattr__(cols[j], get_result[i][j])
            objs_list.append(obj)
        return objs_list


class django_test_books(Model):
    name = CharField('name')

class pytherine_table(Model):
    hyl = CharField('hyl')

if __name__ == '__main__':
    ins = django_test_books(name='funck')
    list = ins.get(name='funck')
    print list[0].name
    # ins.get()
    # ins = pytherine_table()
    # ins.create()
