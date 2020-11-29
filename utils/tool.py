# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/29 13:32]
__purpose__ = 一些抽象工具
"""

import datetime

now = lambda: datetime.datetime.now().strftime('%Y%m%d')


# 生成账号名文件夹
def account_dir_name(account): return now() + f"_{account}"


# 任务表格名
def task_xlsx(account): return "task_" + now() + f"_{account}.xlsx"


# 联系人表格名
def contact_xlsx(account): return "linkman_" + now() + f"_{account}.xlsx"
