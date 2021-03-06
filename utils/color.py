# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/28 18:19]
__purpose__ = ... 
"""

import logging

from core.settings import LOG_PATH, LOG_LEVEL, LOG_FMT, DATE_FMT

logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL, format=LOG_FMT, datefmt=DATE_FMT)

logger = logging.getLogger("buyu")

color_base = "%s[30;2m%s%s[1m" % (chr(27), '', chr(27)) + "%s[3%s;2m%s%s[0m" % (chr(27), '{color}', '{txt}', chr(27))

# TODO: more color supported
color_map = {
    'black': '0',
    'red': '1',
    'green': '2',
    'yellow': '3',
    'blue': '4',
    'purple': '5',
    'white': '7',
}


def console(txt, color="", with_log=True):
    """
    控制台输出颜色字符
    :param txt:  需要输出的字符
    :param color: 颜色， 参考color_map
    :param with_log: 是否同时记录到日志
    :return: None
    """
    # 输出颜色字符到控制台
    # colored_string = color_base.format(txt=txt, color=color_map.get(color, "7"))
    colored_string = txt  # windows 暂时不考虑颜色
    print(colored_string)
    if with_log:
        # 输出字符到日志
        logger.info(txt)
