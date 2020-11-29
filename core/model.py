# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/27 22:21]
__purpose__ = 数据模型
"""
from contextlib import contextmanager
from collections import Iterable

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Enum, TEXT, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.orm.attributes import InstrumentedAttribute

from core.settings import DATABASE
from utils.color import logger

engine = create_engine("sqlite:///{0}".format(DATABASE), encoding='utf8', echo=False)
meta_data = MetaData(bind=engine)
NA = "N/A"


@contextmanager
def get_session():
    Session = sessionmaker(bind=engine, autocommit=True, autoflush=True, expire_on_commit=False)
    session = Session()
    yield session
    session.close()


def open_session():
    Session = sessionmaker(bind=engine, autocommit=True, autoflush=True, expire_on_commit=False)
    session = Session()
    return session


class Base(object):
    id = Column(Integer, autoincrement=True, primary_key=True, nullable=False)
    account = Column(String(length=20), nullable=False, default=NA, doc="采集账户")

    # TODO: something you want do

    @classmethod
    def get_total_query_by_account(cls, account):
        """
        获取某个特定账户采集到的所有信息
        :param account:
        :return:
        """
        with get_session() as session:
            return session.query(cls).filter_by(cls.account == account).all()


BaseModel = declarative_base(bind=engine, name='BaseModel', metadata=meta_data, cls=Base)


class Account(BaseModel):
    """
    帐密信息
    """
    __tablename__ = "account"
    password = Column(String(length=64), nullable=False, default=NA, doc="密码")


class Task(BaseModel):
    """
    任务信息
    """
    __tablename__ = "task"
    task_id = Column(String(length=20), nullable=False, default=NA, doc="任务ID（必填）")
    task_num = Column(String(length=20), nullable=False, default=NA, doc="任务编号（必填）")
    customer_name = Column(String(length=64), nullable=False, default=NA, doc="客户姓名（必填）")
    id_num = Column(String(length=18), nullable=False, default=NA, doc="身份证号码（必填）")
    total_money = Column(Float(precision=10, decimal_return_scale=2), nullable=False, default=0.00, doc="总逾期费用（必填）")
    clear_total = Column(Float(precision=10, decimal_return_scale=2), nullable=False, default=0.00, doc="提前结清金额（必填）")
    customer_id = Column(String(length=20), nullable=False, default=NA, doc="客户ID（必填）")


class Contact(BaseModel):
    """
    联系人信息
    """
    __tablename__ = "contact"
    contact_id = Column(String(length=20), nullable=False, default=False, doc="联系人ID（必填）")
    customer_id = Column(String(length=20), nullable=False, default=NA, doc="客户ID（必填）")
    contact_name = Column(String(length=64), nullable=False, default=NA, doc="联系人姓名（必填）")
    id_num = Column(String(length=18), nullable=False, default=NA, doc="证件号（必填）")
    phone = Column(String(length=20), nullable=False, default=NA, doc="电话号码（必填）")
    relationship = Column(String(length=64), nullable=False, default=NA, doc="联系人关系（必填）")
