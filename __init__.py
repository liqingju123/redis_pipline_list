# -*- coding: utf-8 -*-


import redis
import  random
from urllib import urlopen
import urllib2 
import re
import sys
import haodf_doctor_inf_bs4
import xlwt

#设置连接实例

def get_dortor_url():
    host_redis = redis_client()
    list_host = host_redis.lrange('xingshi_list', 0, -1)
    for one_list_host in list_host:
        search_haodaifu(one_list_host, host_redis)

def redis_client():
    pool = redis.ConnectionPool(host='10.10.8.16', port='6379',password='lqj123')
    return redis.Redis(connection_pool=pool) # host_redis.rpush('listone', '2')

#测试读取数据
def getlpop():
    host_redis =redis_client()
    while True:
        onelist_itmes = host_redis.lpop('listone_text') #获取随机数组 从左侧弹出数据
        if onelist_itmes:
            print onelist_itmes




#测试插入数据，保证写入数据不重复
def setrpush():
    host_redis =redis_client()
    while True:     
        rand_value =random.randint(0,10000)#用于生成测试数字
        instal_retue =host_redis.sadd('listone_set',rand_value);#保证写入数据不重复 
        if instal_retue:
            host_redis.rpush('listone',rand_value) #写入 从未写入的数据 从右侧写入数据
     
def get_html(site):
    print site
    try:
        hdr = {'User-Agent': 'Mozilla/6.0', 'Content-Type':'text/html; charset=gbk', 'Content-Encoding':'gzip'}
        req11 = urllib2.Request(site, headers=hdr)
        data = urllib2.urlopen(req11, timeout=40)
        page = data.read()
        page1 = page.decode('gbk','ignore').encode('utf-8')
        return page1
    except Exception, e:
        print e
        return '错误'


def search_haodaifu(search_txt,redisclient):
    for index in range(50000):
        index=index+1
        search_html = get_html('http://so.haodf.com/index/search?type=doctor&p=%d&kw=%s' % (index,urllib2.quote(search_txt.decode(sys.stdin.encoding).encode('gbk'))))
        search_all_doctor = re.findall('<a href=".*?">专家\((.*?)\)</a>', search_html)
        print len(search_all_doctor)
        if len(search_all_doctor)>0 and int(search_all_doctor[0]) <=(10*(index-1)) :
            print '返回了'
            return        
        search_all_doctor = re.findall('<a target="_blank" href="(.*?)" class="blue1_link">(.*?)</a>', search_html)
        index_doctor_url =0
        for search_all_doctor_one in search_all_doctor:
            if index_doctor_url %2==0:
                doctor_name =search_all_doctor_one[1].decode('utf8').encode('utf8')
                print doctor_name
                redisclient.sadd('doctor_url_name','%s__%s' %(str(search_all_doctor_one[0]),str(doctor_name)))
                print '%s__%s' %(str(search_all_doctor_one[0]),str(search_all_doctor_one[1]))
            index_doctor_url =index_doctor_url + 1;
    


def get_url_info():
    host_redis =redis_client()
    set_doctor_name =host_redis.smembers('doctor_url_name')
    set_doctor_name_to_list =list(set_doctor_name)
    for one_doctor_name in set_doctor_name_to_list[294840:]:
        try:
            doctor_url= one_doctor_name.split('__')
            doctor_info=haodf_doctor_inf_bs4.print_doctor_infor(doctor_url[0])
            print doctor_info,
            host_redis.lpush('doctor_info',doctor_info)
        finally:
            pass



def write_locat():
    host_redis =redis_client()
    doctor_info_list =host_redis.lrange("doctor_info",0,-1)
    open_txt_data =open('/Users/imac/Downloads/第二次好大夫数据/没有个人网站的.txt','w')
    for one_doctor_info_list in doctor_info_list:
        one_doctor_info_list =one_doctor_info_list.replace('暂未开通个人网站','__暂未开通个人网站').replace('____','__')
        if '错误' not in one_doctor_info_list and '暂无登录名称'  in one_doctor_info_list :
            open_txt_data.write(one_doctor_info_list)
    open_txt_data.close()
    print '结束'
    
    
    
host_redis =redis_client()
txt_doctor_name =open('/Users/imac/Downloads/第二次好大夫数据/错误.txt','r')
txt_doctor_name_to_list =txt_doctor_name.readlines()
for one_doctor_name in txt_doctor_name_to_list[748:]:
        try:
            doctor_url= one_doctor_name.replace('\n','').split('__')
            doctor_info=haodf_doctor_inf_bs4.print_doctor_infor(doctor_url[-1])
            print doctor_info,
            host_redis.lpush('doctor_info_err',doctor_info)
        finally:
            pass
