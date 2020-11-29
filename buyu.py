# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/27 22:13]
__purpose__ = ... 应用入口
"""
from typing import *

import xlrd
from xlwt import Workbook

from utils.color import console
from core.settings import *
from core.model import *


def load_account(path):
    """
    从xlsx读取账号信息入库，方便操作
    :return:
    """
    book = xlrd.open_workbook(path)
    sheets = book.sheets()
    for sheet in sheets:
        for row in range(1, sheet.nrows):
            print(sheet.row_values(row, end_colx=2))


def init():
    console(LOGO, "green")
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    console("开始初始化数据库...")
    meta_data.create_all()
    console("开始读取账号密码...")


if __name__ == '__main__':
    # init()
    # book = Workbook()
    # book.save("xxx")
    pass
