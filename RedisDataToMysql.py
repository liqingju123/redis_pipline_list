# -*- coding: utf-8 -*-
import MySQLdb
from uuid import UUID
import redis

def redis_client():
    pool = redis.ConnectionPool(host='10.10.8.43', port='6379',password='lqj123')
    return redis.Redis(connection_pool=pool) # host_redis.rpush('listone', '2')


conn= MySQLdb.connect(host='127.0.0.1',port = 3306,user='root',passwd='lqj123',db ='doctor',charset="utf8")

cur = conn.cursor()
index_sql ="insert into doctorurl (id,name,url) values (REPLACE(UUID(),'-',''),'%s','%s')"

redis_c =redis_client()
set_doctor_name =redis_c.smembers('doctor_url_name')

for one_list_doctor_url in set_doctor_name:
    print one_list_doctor_url
    one_list_doctor_url_arr = one_list_doctor_url.split('__')
    to_str_name =unicode(str(one_list_doctor_url_arr[1]), 'utf-8')
    print to_str_name
    cur.execute(index_sql % (to_str_name,one_list_doctor_url_arr[0]))

cur.close()
conn.commit()
conn.close()
print '插入完成'
