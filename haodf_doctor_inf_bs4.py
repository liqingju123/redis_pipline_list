# encoding:utf-8

from bs4 import BeautifulSoup
from urllib import urlopen
import urllib2
import time
import sys   
import re



add_url = 'http://www.haodf.com'
def rm_all_pasce(text):
    return text.replace("\n", "").replace("\t", "").replace(' ', '').replace('\r', '').replace('<<收起', '')

def get_html(site):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    req = urllib2.Request(site, headers=hdr)
    data = urllib2.urlopen(req, timeout=4)
    page = data.read()
#     print page
  
    try:
        content_bs4 =BeautifulSoup(page,"html.parser")
        if 'hospital' in site:
            page = page.decode('gbk','ignore').encode('utf-8')
            return  page
        return content_bs4
        print '===请求到了==='
    except Exception, e:
        return '错误' 

# 获取医院大名and小名    
def get_yiyuan_name(one_url):
    daming_yiyuan ='错误'
    yiyuan ='错误'
    try:
#         print one_url
        context = get_html(one_url)
#         print context.get_text()
        if context == '错误':
            return '错误'
        get_yinyuan_list =re.findall(r'<span style="font-size:\d{2}px"><a href="http://www.haodf.com/hospital/.*?">(.*?)</a> </span><span style="font-size:\d{2}px;"></span>',context)
#         get_yinyuan_list = context.find_all('div', {"id":"ltb"})
#         get_yinyuan_list = context.find_all('div')
#         print get_yinyuan_list[0]
        get_yinyuan_list_2 =re.findall(r'<p> <a href="http://www.haodf.com/hospital/.*?">(.*?)</a>\((.*?)\)</p>', context)
#         get_yinyuan_list_2 = context.find_all('div', {"class":"panelA_blue"})
        if len(get_yinyuan_list) == 0 or len(get_yinyuan_list_2) == 0:
            return '错误'

        daming_yiyuan = get_yinyuan_list[0]

        yiyuan = get_yinyuan_list_2[0][0]+'__'+get_yinyuan_list_2[0][1]
    except Exception, e:
        print e
    finally:
        return  daming_yiyuan + '__' + yiyuan  

# 获取 地址 医院 科室信息    
def  get_yiyuan_keshi(context_text):
#     print context_text
#     base_text = context_text.find_element_by_class_name('container').get_attribute('innerHTML')
    context_all_dev = BeautifulSoup(str(context_text), "html.parser")
#     print context_all_dev

    all_a = context_all_dev.find_all("div", {"class":"luj"});
    if len(all_a) == 0:
        return '错误'
    content_a_html = BeautifulSoup(str(all_a[0]), "html.parser")
    content_a_list = content_a_html.find_all("a", {"target":"_blank"});
    if len(content_a_list) < 4:
        return '错误'
    content_a_list = content_a_list[2:]
    one_a_all = str(content_a_list[0].get_text().encode('utf-8')) + '__' + get_yiyuan_name(add_url + str(content_a_list[1]['href'].encode('utf-8')))   + '__' + str(content_a_list[2].get_text().encode('utf-8'))
    return one_a_all

def get_hist(host):
    context = get_html(host)
#     print context
    if '错误' == context or isinstance(context,(str)) :
        return '错误'
    
    javas = context.find_all('script', {'type':'text/javascript'});
    if len(javas) < 2:
        return '错误'

    content_all = str(javas[2].get_text().encode('utf8')).replace('BigPipe.onPageletArrive({"id":"bp_doctor_about","content":"', '').replace('\n","cssList":[],"jsList":{"http:\/\/www.haodf.com\/api\/get_activetime.php?d=[0-9]+":0}});', '');
    content_all = content_all.decode("unicode-escape").encode("utf-8").replace('\\', '')

    get_hist = str(javas[1]).replace('<script type="text/javascript">BigPipe.onPageletArrive({"id":"bp_top","content":"', '').decode("unicode-escape").encode("utf-8").replace('\\', '')

    return get_doctor_info(content_all, get_hist, host) 

def get_doctor_info(base_text, context_text, host):
    context_all_dev = BeautifulSoup(base_text, "html.parser")
    all_text = str(get_yiyuan_keshi(context_text))
#     print 'all_text1==   '+all_text
    
    all_jianjie_zhicheng = context_all_dev.find_all("td", {"valign":"top"})
    home_doctor_url =context_all_dev.find('a', {"class":"blue","target":"_blank"})
    if home_doctor_url:
        home_doctor_url =home_doctor_url.text
        if '.haodf.com' in home_doctor_url:
            all_text =all_text+'__'+str(home_doctor_url)
            home_doctor_login_id=home_doctor_url.replace('http://','').replace('.haodf.com/','')
            all_text =all_text+'__'+str(home_doctor_login_id)
        else:
            all_text =all_text+'暂未开通个人网站__暂无登录名称'
    else:
        all_text =all_text+'__暂未开通个人网站__暂无登录名称'
    if len(all_jianjie_zhicheng) < 6:
        return '错误'
#     print "=====   "+all_jianjie_zhicheng[7].get_text()
    zhicheng = rm_all_pasce(str(all_jianjie_zhicheng[6].get_text().encode('utf-8')))
    if '师' not in zhicheng:
        zhicheng = rm_all_pasce(str(all_jianjie_zhicheng[7].get_text().encode('utf-8')))
    all_text = str(all_text) + '__' + zhicheng.replace('师', '师__1')
   
    
    all_jianjie_name = context_all_dev.find_all("div", {"class":"nav"})
    all_text = all_text + '__' + rm_all_pasce(str(all_jianjie_name[0].h1.a.get_text().encode('utf-8')))
   
    # nav
    all_jianjie = context_all_dev.find_all("div", {"id":"full"})
#     print context_all_dev
    all_jianjie_shanchang = context_all_dev.find_all("div", {"id":"full_DoctorSpecialize"})
    if len(all_jianjie_shanchang) == 0:
        all_jianjie_shanchang = context_all_dev.find_all("div", {"id":"truncate_DoctorSpecialize"})
    if len(all_jianjie_shanchang) == 0:
        print '错误'
    else:
        all_text = all_text + '__' + rm_all_pasce(str(all_jianjie_shanchang[0].get_text().encode('utf-8')))
     
   
    if len(all_jianjie) == 0:
        one_zhijiye = context_all_dev.find_all('td', {'colspan':'3', 'valign':'top'})
        all_text = all_text + '__' + rm_all_pasce(str(one_zhijiye[1].get_text().encode('utf-8')))
      
    else:
        for one_div in all_jianjie:
            text_str = str(one_div.get_text().encode('utf-8'));
            all_text = all_text + '__' + rm_all_pasce(text_str)
         
   
    return all_text



    
    
 
def print_doctor_infor(host_stat):
    input_str = str(get_hist(host_stat)) + '__' + str(host_stat.encode('utf8')) + '\n'
    return input_str   
 
# print get_html('http://www.haodf.com/hospital/DE4roiYGYZwaJqBdz13dpO1a1.htm')
 
# print get_hist('http://www.haodf.com/doctor/DE4r0Fy0C9LuwYiOnQ9GlCdeozGolC54J.htm')  
# print get_hist('http://www.haodf.com/doctor/DE4r08xQdKSLfirpoozM21bXlzuR.htm')  
# print get_hist('http://www.haodf.com/doctor/DE4r0BCkuHzdegoy8FXkFGpEHP0h6.htm')  


