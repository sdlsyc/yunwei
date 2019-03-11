#coding=utf-8
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import sqlite3
import threading
import os.path
aukey=''
ausecret=''
areaname="cn-hangzhou"
areadomain="edas.cn-hangzhou.aliyuncs.com"
termnum="2testcms"                    #2test
appflag=1    #0关闭，1开启
def startapp(appid):
    #print(appid)
    client = AcsClient(aukey, ausecret, areaname)
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_domain("edas.cn-hangzhou.aliyuncs.com")
    #request.set_domain(areadomain)报错
    request.set_version('2017-08-01')
    request.add_query_param("RegionId", areaname)
    request.add_query_param('AppId', appid)
    request.set_uri_pattern('/pop/v5/changeorder/co_start')
    response = client.do_action(request)
    print(str(response, encoding='utf-8'))

def stopapp(appid):
    #print(appid)
    client = AcsClient(aukey, ausecret, areaname)
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_domain("edas.cn-hangzhou.aliyuncs.com")
    #request.set_domain(areadomain)报错
    request.set_version('2017-08-01')
    request.add_query_param("RegionId", areaname)
    request.add_query_param('AppId', appid)
    request.set_uri_pattern('/pop/v5/changeorder/co_stop')
    response = client.do_action(request)
    print(str(response, encoding='utf-8'))
if __name__=="__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ADD_LIST = os.path.join(BASE_DIR, 'edas.db')
    conn = sqlite3.connect(ADD_LIST)
    cursor = conn.cursor()
    cursor.execute('select appid,appname from apps where env=?',(termnum,))
    values = cursor.fetchall()
    cursor.close()
    conn.close()
    print(values)
    progroup={}
    if appflag == 0:
        operfunc=stopapp
    else:
        operfunc=startapp

    for appinfo in values:
        threadname=appinfo[1]
        progroup[threadname] = threading.Thread(name='th'+appinfo[1],target=operfunc,args=(appinfo[0],))
        print("%s ok" % appinfo[1])
        progroup[threadname].start()
