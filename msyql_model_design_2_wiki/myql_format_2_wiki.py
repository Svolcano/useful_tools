import pymysql
import json
import os
import sys
import logging

logger = logging.getLogger(__name__)


class MyDB(object):
    def __init__(self, host, user, pwd, port, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.db = db
        self.my_conn = pymysql.Connect(
            host=host,
            user=user,
            password=pwd,
            database=db,
            charset='utf8mb4',
            port=port,
        )

    def __enter__(self):
        # ttysetattr etc goes here before opening and returning the file object
        self.my_conn = pymysql.Connect(
            host=self.host,
            user=self.user,
            password=self.pwd,
            database=self.db,
            charset='utf8mb4',
            port=self.port,
        )
        return self

    def __exit__(self, type, value, traceback):
        # Exception handling here
        self.close()

    def query(self, sql, args=[]):
        try:
            with self.my_conn.cursor() as cur:
                cur.execute(sql, args)
                return cur.fetchall()
        except Exception as e:
            logger.error(e, exc_info=True)
        return []

    def query_one(self, sql, args=None):
        try:
            with self.my_conn.cursor() as cur:
                cur.execute(sql, args)
                return cur.fetchone()
        except Exception as e:
            logger.error(e, exc_info=True)
        return []

    def execute(self, sql, args=None):
        try:
            with self.my_conn.cursor() as cur:
                cur.execute(sql, args)
                self.my_conn.commit()
                return True
        except Exception as e:
            logger.error(e, exc_info=True)
            self.my_conn.rollback()
            return False

    def executemany(self, sql, data=[]):
        try:
            with self.my_conn.cursor() as cur:
                cur.executemany(sql, data)
                self.my_conn.commit()
                return True
        except Exception as e:
            logger.error(e, exc_info=True)
            self.my_conn.rollback()
        return False

    def close(self):
        try:
            self.my_conn.close()
        except Exception as e:
            logger.error(e, exc_info=True)


def get_new_handler():
    conn = MyDB(host='127.0.0.1',
                port=3306,
                user='root',
                pwd='1234qwer',
                db='hubble2')
    return conn

table_style = '''
<style>
    table.customers {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
    }


    .customers td, #customers th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
    }

    .customers tr:nth-child(even) {
        background-color: #dddddd;
    }
</style>
'''
table_container = '''
<br/>
<h1>Table: %s</h1>
<table class="customers">
    <tbody>
        <tr>
            <th>字段</th>
            <th>类型</th>
            <th>Collation</th>
            <th>可以为Null</th>
            <th>索引</th>
            <th>默认值</th>
            <th>Extra</th>
            <th>Comment</th>
        </tr>
        %s
    </tbody>
</table>
<br/>
'''
row_container = '''
<tr>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>
'''

db_handler = get_new_handler()
table_names = db_handler.query('show tables')
table_list = []
for t in table_names:
    table_name = t[0]
    column_infos = db_handler.query('show full columns from {}'.format(table_name))
    rows = []
    for one in column_infos:
        field, type, collation, null, key, default, extra, _, comment = one
        row = row_container % (field, type, collation or '', null, key, default, extra, comment)
        rows.append(row)
    table = table_container % (table_name, '\n'.join(rows))
    table_list.append(table)
html = "{}\n{}\n".format(table_style, '\n'.join(table_list))
with open('a.txt', 'w') as wh:
    wh.write(html)