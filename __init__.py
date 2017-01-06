# -*- coding: utf-8 -*-


import redis
import  random


#设置连接实例
def redis_client():
    pool = redis.ConnectionPool(host='10.10.8.43', port='6379',password='lqj123')
    return redis.Redis(connection_pool=pool) # host_redis.rpush('listone', '2')

#测试读取数据
def getlpop():
    host_redis =redis_client()
    while True:
        onelist_itmes = host_redis.lpop('list_url') #获取随机数组 从左侧弹出数据
        if onelist_itmes:
            print onelist_itmes




#测试插入数据，保证写入数据不重复
def setrpush():
    host_redis =redis_client()
    while True:     
        rand_value =random.randint(0,10000000)#用于生成测试数字
        instal_retue =host_redis.sadd('list_url_set',rand_value);#保证写入数据不重复 
        if instal_retue:
            host_redis.rpush('list_url',rand_value) #写入 从未写入的数据 从右侧写入数据
     

getlpop()
