# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/29 14:58]
__purpose__ = ... 
"""
import requests
from core.settings import *

from core.collectors import TaskCollector, ContactCollector

if __name__ == '__main__':
    b = TaskCollector("xxx")
    # b.login()
    # res = requests.get(f"{BASE_URL}/snucs/#/login")
    # print(res.text)
    b.login()
    b.collect()
    # b.close()
