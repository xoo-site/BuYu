# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/28 18:00]
__purpose__ = 一些配置文件
"""
import os
import logging

# 当前软件版本
VERSION = "1.0.0"

# 项目根目录
BASE_DIR = os.getcwd()

# 配置文件路径
CONF_PATH = os.path.join(BASE_DIR, "config.yml")

# 日志保存路径
LOG_PATH = os.path.join(BASE_DIR, 'buyu.log')

# 日志级别
LOG_LEVEL = logging.INFO

# 日志保存格式
LOG_FMT = '[%(name)s %(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s'

# 时间序列化格式
DATE_FMT = "%Y-%m-%d %H:%M:%S"

# 数据库
DATABASE = os.path.join(BASE_DIR, "db.sqlite3")

# 脚本运行时的logo
LOGO = r"""
===============苏宁捕逾系统数据导出工具===========
   ___ ___  _ __   __ _ _ __
  / __/ _ \| '_ \ / _` | '_ \       作者: Jeyrce.Lu
 | (_| (_) | | | | (_| | | | |      版本: %s
  \___\___/|_| |_|\__,_|_| |_|      祝你好运!
""" % VERSION

# api基本地址
BASE_URL = "https://buyu.suning.com"

# 默认请求头
HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

# 账号信息表格文件
ACCOUNT_XLSX = os.path.join(BASE_DIR, "账号.xls")
