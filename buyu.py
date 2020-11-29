# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/27 22:13]
__purpose__ = ... 应用入口
"""
import sys
from typing import *

import xlrd
from xlwt import Workbook

from utils.color import console
from core.settings import *
from core.model import *
from utils.tool import account_dir_name
from core.collectors import *


def load_account(path):
    """
    从xlsx读取账号信息入库，方便操作
    :return:
    """
    console("开始读取账号密码...")
    book = xlrd.open_workbook(path)
    sheets = book.sheets()
    succeed = 0
    failed = 0
    accounts = []
    for sheet in sheets:
        for row in range(1, sheet.nrows):
            data = sheet.row_values(row, end_colx=2)
            # xlrd 可能会把数字默认变成浮点数
            parsed_data = [str(int(value)) if isinstance(value, (float, int)) else str(value).strip() for value in data]
            with get_session() as session:
                try:
                    session.add(Account(account=parsed_data[0], password=parsed_data[1]))
                    session.flush()
                except Exception as e:
                    failed += 1
                    logger.exception(e)
                else:
                    succeed += 1
                    accounts.append(parsed_data[0])
            data_dir = os.path.join(BASE_DIR, account_dir_name(parsed_data[0]))
            if not os.path.exists(data_dir):
                os.mkdir(data_dir)
    console(f"读取账号信息成功[{succeed}]条，失败[{failed}]条.")
    return accounts


def init():
    console(LOGO, "green")
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    console("开始初始化数据库...")
    meta_data.create_all()


def collect(account, speed):
    """
    采集每个账号中的数据并制作excel
    :param accounts:
    :return:
    """
    clazz = [
        TaskCollector,
        ContactCollector,
    ]
    for claz in clazz:
        claz(account).run()


if __name__ == '__main__':
    # 初始化
    init()
    accounts = load_account(ACCOUNT_XLSX)
    # while True:
    #     speed = input("输入采集速度回车继续[1-10]: ")
    #     try:
    #         speed = int(speed)
    #     except Exception as e:
    #         console("请输入一个合理的采集速度")
    #         continue
    #     else:
    #         if speed < 1 or speed > 10:
    #             console("请输入一个合理的采集速度")
    #             continue
    #         else:
    #             break
    for account in accounts:
        collect(account, 10)
    sys.exit(0)
