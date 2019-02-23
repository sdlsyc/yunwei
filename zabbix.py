# /usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
import json
import os

## user config here
ip = '8.8.8.8'
user = "Admin"
password = "passwd"

## user config end

class ZabbixApi:
    def __init__(self, ip, user, password):
        self.url = 'http://8.8.8.8/api_jsonrpc.php'  #修改为你自己的地址
        self.headers = {"Content-Type": "application/json",
                        }
        self.user = user
        self.password = password
        self.auth = self.__login()

    def __login(self):
        '''
        zabbix登陆获取auth
        :return: auth  #  样例bdc64373690ab9660982e0bafe1967dd
        '''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.user,
                "password": self.password
            },
            "id": 10,
            # "auth": 'none'
        })
        try:
            response = requests.post(url=self.url, headers=self.headers, data=data, timeout=5)
            # {"jsonrpc":"2.0","result":"bdc64373690ab9660982e0bafe1967dd","id":10}
            auth = response.json().get('result', '')
            return auth
        except Exception as e:
            print("Login error check: IP,USER,PASSWORD")
            raise Exception

    def host_get(self, hostname=''):
        '''
        获取主机。
        :param hostName: zabbix主机名不允许重复。（IP允许重复）。#host_get(hostname='gateway1')
        :return: {'jsonrpc': '2.0', 'result': [], 'id': 21}
        :return: {'jsonrpc': '2.0', 'result': [{'hostid': '10277', ... , 'host': 'gateway', ...}], 'id': 21}
        '''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {"output": "extend",
                       "filter": {"host": hostname},
                       },
            "id": 21,
            "auth": self.auth
        })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=5)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            #print(response.json())
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。
        except Exception as e:
            print("HOST GET ERROR")
            raise Exception

    def hostgroup_get(self,hostGroupName=''):
        '''
        获取主机组
        :param hostGroupName:
        :return: {'jsonrpc': '2.0', 'result': [{'groupid': '15', 'name': 'linux group 1', 'internal': '0', 'flags': '0'}], 'id': 1}
        '''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": hostGroupName
                }
            },
            "auth": self.auth,
            "id": 1,
            })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=5)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。

        except Exception as e:
            print("HOSTGROUP GET ERROR")
            raise Exception

    def hostgroup_create(self,hostGroupName=''):
        if len(self.hostgroup_get(hostGroupName).get('result'))==1:
            print("无需创建，hostgroup存在")
            return 100
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostgroup.create",
            "params": {
                "name": hostGroupName
            },
            "auth": self.auth,
            "id": 1
            })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=5)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            return response.json()

        except Exception as e:
            print("HOSTGROUP CREATE ERROR")
            raise Exception

    def template_get(self,templateName=''):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": templateName
                }
            },
            "auth": self.auth,
            "id": 50,
            })
        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=5)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            return response.json()

        except Exception as e:
            print("Template GET ERROR")
            raise Exception

    def host_create(self,hostname,visiblename,hostip,hostGroupName,templateName):
        '''
        创建host，并分配分组，关联模版
        host_create('host3','visible name','1.1.1.1','group1,group2...','template1,template2...')
        '''
        # 判断主机名是否重复。 zabbix不允许主机名重复
        find_hostname=self.host_get(hostname)
        if  len(find_hostname.get('result')):
            print("###recheck### hostname[%s] exists and return"%hostname)
            return 1

        # 判断template是否存在，不存在退出。 否则初始化备用
        template_list = []
        for t in templateName.split(','):
            find_template = self.template_get(t)
            if not len(find_template.get('result')):
                # template不存在退出 # 一般因为输错关系
                print("###recheck### template[%s] not find and return " %t)
                return 1

            tid=self.template_get(t).get('result')[0]['templateid']
            #print(tid)
            template_list.append({'templateid':tid})

        # 判断hostgroup是否存在。 不存在则创建。 并初始化hostgroup_list备用
        hostgroup_list=[]
        for g in hostGroupName.split(','):
            find_hostgroupname = self.hostgroup_get(g)
            if not len(find_hostgroupname.get('result')):
                # hostgroupname 不存在，创建
                self.hostgroup_create(g)
            gid=self.hostgroup_get(g).get('result')[0]['groupid']
            hostgroup_list.append({'groupid':gid})

        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostname,
                "name": visiblename,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": hostip,
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": hostgroup_list,
                "templates": template_list,
            },
            "auth": self.auth,
            "id": 1
            })

        try:
            response = requests.get(url=self.url, headers=self.headers, data=data, timeout=5)
            # hosts_count=len(response.json().get('result',''))
            # print('l',hosts)
            print("执行返回信息： 添加HOST[%s,%s]完成" % (hostname,visiblename))
            return response.json()   # len(ret.get('result'))为1时获取到，否则未获取到。

        except Exception as e:
            print("HOST CREATE ERROR")
            raise Exception

if __name__ == '__main__':
    try:
        zabbix = ZabbixApi(ip, user, password)
        print("...login success...")


        # 添加主机单台
        #zabbix.host_create('host7','1.1.1.1','gp1 test,gp2 test','Template App FTP Service,Template App HTTP Service')

        #批量添加主机，从文本serverlist.txt
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ADD_LIST= os.path.join(BASE_DIR,'serverlist.txt')
        with open(ADD_LIST,'r',encoding='utf-8') as f:
            for line in f:
                if len(line.strip()): #跳过空行
                    serverinfo=line.strip().split('#')

                    #print(serverinfo)
                    zabbix.host_create(serverinfo[0],serverinfo[1],serverinfo[2],serverinfo[3],serverinfo[4])

    except Exception as e:
        print(e)