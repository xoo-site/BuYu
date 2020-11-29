# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/27 22:22]
__purpose__ = 数据文件导出
"""
from typing import *

from xlwt import Workbook

from core.model import BaseModel, get_session, NA
from core.model import Task, Contact
from utils.color import console


class BaseSerializer(object):
    # 需要导出的表, 即model.py中定义的表
    __model__: BaseModel.__class__ = None
    # 需要导出的字段和表头, 为保证顺序此处必须显式指定所有要导出的字段
    # 支持动态扩展字段, 例如
    #     __fields__ = (("", "xx"),)
    #     如果__model__中没有xx这个字段，则可以定义一个_get_xx(item)方法动态获取, 其中item是__model__的实例
    __fields__: Tuple[Tuple[AnyStr, AnyStr]] = ((),)
    __sheet__: AnyStr = ""  # 生成的sheet名, 为空则默认为表名
    sheet_size = 10000

    def __init__(self, book: Workbook, account: str = None):
        self.book = book  # 从外部传过来的工作簿
        self.account = account  # 传入账户则导出特定账户的数据

    def get_sheet(self, sheet_name=None):
        """
        获取当前写入的sheet
        """
        assert isinstance(self.__sheet__, str), "Not supported sheet name"
        sheet_name = sheet_name or self.__sheet__ or self.__model__.__tablename__
        try:
            sheet = self.book.get_sheet(sheet_name)
        except:
            sheet = self.book.add_sheet(sheet_name, cell_overwrite_ok=True)
        return sheet

    def get_queryset(self):
        """
        需要导出的数据集合，默认为__model__表中所有记录, 如果需要筛选则覆盖此方法
        """
        assert self.__model__.__class__.__name__ == BaseModel.__class__.__name__, "Expected a %s __model__, but got %s" % (
            BaseModel.__class__.__name__,
            self.__model__.__class__.__name__,
        )
        with get_session() as session:
            if not self.account:
                queryset = session.query(self.__model__).all()
            else:
                queryset = self.__model__.get_total_query_by_account(self.account)
            return queryset

    def write_title(self, sheet):
        """
        写入表头
        """
        row = 0
        col = 0
        for field in self.__fields__:
            value = NA
            if field[0]:
                value = field[0]
            elif hasattr(self.__model__, field[1]):
                value = getattr(self.__model__, field[1]).__doc__
            sheet.write(row, col, value)
            col += 1

    def write_data(self, sheet, queryset):
        """
        写入数据
        """
        row = 1
        for item in queryset:
            col = 0
            for field in self.__fields__:
                # 首先从实例属性获取
                func = getattr(self, "_get_%s" % field[1], None)
                if hasattr(item, field[1]):
                    value = getattr(item, field[1])
                # 其次查看serializer是否实现了_get_<字段>方法
                elif callable(func):
                    value = func(item)
                else:
                    value = NA
                sheet.write(row, col, value)
                col += 1
            row += 1
        return sheet

    def serialize(self):
        """
        导出的具体实现
        """
        console(f"Model {self.__class__.__name__} excel making".center(80, "="))
        queryset = self.get_queryset()
        num = (len(queryset) // self.sheet_size) + 1
        for i in range(0, num):
            sheet = self.get_sheet(f"sheet{i}")
            self.write_title(sheet)
            self.write_data(sheet, queryset[i * self.sheet_size:(i + 1) * self.sheet_size])
        return self.book


class TaskSerializer(BaseSerializer):
    __model__ = Task
    __fields__ = (
        # (表头，字段), 如果表头为空则取model定义时的doc
        ("", "task_id"),
        ("", "task_num"),
        ("", "customer_name"),
        ("", "id_num"),
        ("", "total_money"),
        ("", "clear_total"),
        ("", "customer_id"),
    )
    __sheet__ = Task.__tablename__


class ContactSerializer(BaseSerializer):
    __model__ = Contact
    __fields__ = (
        ("", "contact_id"),
        ("", "customer_id"),
        ("", "contact_name"),
        ("", "id_num"),
        ("", "phone"),
        ("", "relationship"),
    )
    __sheet__ = Contact.__tablename__
