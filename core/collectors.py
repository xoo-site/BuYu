# coding=utf-8
"""
__author__  = Jeyrce.Lu [Jeyrce@gmail.com] [https://www.lujianxin.com/] [2020/11/29 13:55]
__purpose__ = ... 
"""
import os
import urllib3
import time

urllib3.disable_warnings()

import requests
from requests.cookies import RequestsCookieJar

from core.serializer import *
from core.settings import *
from utils.tool import account_dir_name, contact_xlsx, task_xlsx
from utils.color import logger
from core.model import *
from utils.tool import now


class BaseCollector(object):
    """
    采集数据入库并制作excel
    """
    serializer_class: BaseSerializer.__class__ = None
    page_size = 100

    def __init__(self, account, sleep=0):
        self.account = account
        self.auth_cookie = None
        self.session = open_session()
        self.sleep = sleep

    def book_file(self):
        """
        保存后的文件名
        :return:
        """
        raise NotImplementedError

    @property
    def passwd(self):
        """
        从数据库获取密码
        :return:
        """
        account = self.session.query(Account).filter_by(account=self.account).all()
        if account:
            return account[0].password
        return ""

    def login(self):
        """
        :return:
        """
        path = "/snucs/login"
        data = {
            "loginNo": self.account,
            "password": self.passwd,
        }
        cookies = {
            # 'route': 'b64f3e5c271e7c217c428b8dfa47f124',
            # '_snsr': 'direct%7Cdirect%7C%7C%7C',
            # '_snma': '1%7C160656345523598106%7C1606563455235%7C1606563455235%7C1606563455514%7C1%7C1',
            # '_snmp': '160656345498590389',
            # '_snmb': '160656345552049755%7C1606563455533%7C1606563455520%7C1',
            # '_snvd': '1606563455982rWay8tAQrPH',
            # 'SN_CITY': '130_571_1000323_9315_01_12499_2_0',
            # 'cityId': '9315',
            # 'districtId': '12499',
            # 'streetCode': '5710199',
            # 'cityCode': '571',
            # 'authId': 'siBE010442070296EA800471E2BF92FE6D',
            # 'secureToken': 'B18462211D47BB58585A3A74278E8924',
            # 'tradeMA': '32',
            # 'totalProdQty': '0',
            # 'token': 'd60c5045-890e-4969-8bd8-fd07c3ba5805',
            # 'hm_guid': '7e7b64d3-5a59-4f09-8500-6f78e47eed9d',
            # '_df_ud': 'fd140c6f-3513-44a5-a64d-acb4dbb3f08c',
        }
        # cookie_jar = RequestsCookieJar()
        # for k, v in cookies.items():
        #     cookie_jar.set(k, v, domain="buyu.suning.com")
        try:
            response = requests.post(
                f"{BASE_URL}{path}",
                headers=HEADERS,
                json=data,
                verify=False,
            )
            assert response.status_code == 200, response.status_code
            console(response.json())
        except Exception as e:
            logger.exception(e)
            console(f"[ ERROR ]账户[{self.account}]登录失败，请检查用户名和密码")
        else:
            console(f"[ OK ]账户[{self.account}]登录成功.")
            self.auth_cookie = response.cookies

    def collect(self):
        """
        具体采集实现逻辑
        :return:
        """
        raise NotImplementedError

    def serialize(self):
        """
        制作excel
        :return:
        """
        serializer = self.serializer_class(Workbook(), self.account)
        book = serializer.serialize()
        if os.path.exists(self.book_file()):
            os.rename(self.book_file(), f"{self.book_file()}_bak_{now()}")
        book.save(self.book_file())

    def close(self):
        try:
            self.session.close()
        except Exception as e:
            logger.exception(e)

    def run(self):
        console(f"账号[{self.account}]采集任务开始")
        self.login()
        cnt = self.collect()
        console(f"[ OK ]获取到[{cnt}]条数据")
        self.serialize()
        console(f"[ OK ]表格{self.book_file()}制作完毕")
        self.close()


class TaskCollector(BaseCollector):
    """
    任务信息采集类
    """
    serializer_class = TaskSerializer

    def book_file(self):
        data_dir = account_dir_name(self.account)
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        return os.path.join(
            data_dir,
            task_xlsx(self.account),
        )

    def page_detail(self, page_num):
        """
        返回每页响应信息
        :return:
        """
        path = "/snucs/task/page-list"
        json_data = {"merge": True, "programPolicy": "", "finaCodeList": [], "customerName": "", "taskBatchDate": "",
                     "certiNo": "", "phone": "", "taskOwnerIdList": [], "tradeSource": "", "handleStatusList": [],
                     "taskAllocateStatus": "", "handleType": "", "lastContactResult": "", "repayStatus": "",
                     "minTelCount": "", "maxTelCount": "", "minOverdueAmount": "", "maxOverdueAmount": "",
                     "minOverdueDate": "", "maxOverdueDate": "", "dCreateTime": [], "lastAllocateTime": [],
                     "taskStartOverdueDate": [], "nextContactTime": [], "caseFinishTime": [], "firstHandleDate": "",
                     "firstHandleStatus": "", "finishedShowed": True, "prodCodeList": [], "tagId": "", "isToOut": "",
                     "collRepayAmount": "", "currentOwnerCom": "", "outBatchName": "", "minOverduePrincipal": "",
                     "maxOverduePrincipal": "", "minCollRepayPrincipal": "", "maxCollRepayPrincipal": "",
                     "tradeIndex": "",
                     "predictName": "", "cardList": [], "tradeIndexList": [], "city": [], "province": [],
                     "customerGroupTag": "", "customerNo": "", "customerNoList": [], "tagIdsCon": [], "tagIdsDel": [],
                     "styleCon": "", "styleDel": "", "style": "overdue", "sortKey": "watermark_alpha",
                     "dalPage": {"pageSize": self.page_size, "currentPage": page_num},
                     "orderByClause": " handle_type asc ", "sortedColumn": "", "sortedType": ""}
        try:
            res = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=json_data, cookies=self.auth_cookie,
                                verify=False)
            assert res.status_code == 200, res.status_code
            data = res.json()
        except Exception as e:
            logger.exception(e)
        else:
            if data.get("ret") == "0000":
                return data.get("data")
        return None

    def collect(self):
        cnt = 0
        if not self.auth_cookie:
            return cnt
        # 获取第一页， 之后所有的页码直接遍历
        data = self.page_detail(1)
        # page = {
        #     "count": 388,  # 总数量
        #     "currentPage": 2,  # 当前页码
        #     "index": 10,  # 最后一条的索引？
        #     "pageSize": 10,  # 每页条数
        #     "pages": 39,  # 总页数
        # }
        # 查询所有页
        if not data:
            return cnt
        pages = int(data.get("page", {}).get("pages", 1))
        for p in range(1, pages + 1):
            per_page = self.page_detail(p)
            _list = per_page.get("list", [])
            for l in _list:
                task_info = l.get("taskInfo", [])
                for task_detail in task_info:
                    """
                    allocateTimeStr: "20201101155546"
                    blackFlag: false
                    ccmsOutBatchId: null
                    certiNo: "511302197910xxxxxx"
                    certiType: "1011"
                    city: "9269"
                    cityName: "南充市"
                    clearBaseAmount: 4513.04
                    clearStatus: "0"
                    collRepayAmount: 4513.04
                    collRepayDemurrage: 0
                    collRepayInterest: 212.59
                    collRepayOther: 0
                    collRepayPrincipal: 4017.21
                    currentOwnerCom: "2019112702"
                    currentOwnerComName: "常州合雅网络科技有限公司"
                    customerGroupTag: "999"
                    customerId: 785537
                    customerName: "张宁"
                    customerNo: null
                    dCreateTime: 1561742367000
                    dCreateUser: "CCMS_DATA_CASE_TASK"
                    dUpdateTime: 1606612398000
                    dUpdateUser: "system"
                    deadline: "2020-12-01"
                    distModel: "1"
                    expendDay: 30
                    finishTime: "2018-12-03 00:08:14"
                    firstHandleDate: "20201101"
                    firstHandleStatus: "0001"
                    firstTelTime: "2020-04-08 09:15:58"
                    handleStatus: "0001"
                    handleStatusDesc: "未处理"
                    handleType: "0001"
                    handleTypeDesc: "首催任务"
                    hasChildren: true
                    id: 3860353
                    isRetain: "N"
                    isToOut: "2"
                    lastAllocateTime: "2020-11-01 15:58:14"
                    lastAllocator: 105209
                    lastAllocatorName: "曹俊"
                    lastContactResult: "0004"
                    lastContactResultDesc: "无人接听"
                    lastContactTime: "2020-10-29 19:06:47"
                    loanPrincipal: 56082
                    maxOverdueDate: 237
                    msgCount: 0
                    nextContactTime: ""
                    noFee: 0
                    noPenalty: 0
                    outBatchName: "201101M7-12"
                    outBatchNo: 20201101016395
                    outContactStatus: null
                    ovdueCompoundInterest: 0
                    ovdueFee: 0
                    overdueAmount: 4513.04
                    overdueBillCount: 0
                    overdueDate: 237
                    overdueDemurrage: 283.24
                    overdueInterest: 212.59
                    overdueLoanCount: 11
                    overdueOther: 0
                    overduePricipal: 4017.21
                    paymentType: "01"
                    policyCode: null
                    predictBatchId: null
                    predictName: null
                    prodCdOuter: null
                    prodCode: "RXD"
                    prodName: "任性贷"
                    programCode: null
                    province: "230"
                    provinceName: "四川省"
                    remainedAmount: 0
                    remainedPrincipal: 0
                    repayStatus: "0001"
                    returnTime: null
                    riskGrade: null
                    score: 23
                    score1: 0
                    sourceOwnerCom: "sncs"
                    sourceOwnerComName: "苏宁金融科技有限公司"
                    startTaskTime: "20201101152739"
                    sumCleanAmt: 43433.95
                    tagList: "内-离职,苏宁金融"
                    tags: [{id: 31, markName: "[内部员工-离职]", markShorter: "内-离职", markColour: "#ffd700", markStatus: 1,…},…]
                    taskAllocateStatus: "0003"
                    taskBatchDate: "2018-01-01"
                    taskBatchNo: "201903085113021979"
                    taskOverdueFrequency: 4
                    taskOwnerId: 105241
                    taskOwnerName: "李梦婷"
                    taskOwnerTelNo: null
                    taskStartOverdueDate: "2020-04-05"
                    telCount: 42
                    telNo: "15298212694"
                    tempProgramCode: null
                    temporaryOutBatchNo: 0
                    thisprdAccumShdpayCompoundInterest: 0
                    thisprdAccumShdpayPenaltyInterest: 283.24
                    tradeCollStatus: 2
                    tradeIndex: null
                    tradeSource: "002"
                    tradeSourceDesc: "苏宁小贷"
                    updateOwnerIdTime: null
                    verifyFlag: null
                    version: 52
                    """
                    d = dict(
                        account=self.account,
                        task_id=task_detail.get("id", NA),
                        task_num=task_detail.get("taskBatchNo", NA),
                        customer_name=task_detail.get("customerName", NA),
                        id_num=task_detail.get("certiNo"),
                        total_money=task_detail.get("overdueAmount", NA),
                        clear_total=task_detail.get("clearBaseAmount", NA),
                        customer_id=task_detail.get("customerId", NA),
                    )
                    self.session.add(Task(**d))
                    self.session.flush()
                    cnt += 1
                    console(f"获取到任务信息: {d['customer_name']}-{d['customer_id']}")
            time.sleep(self.sleep)
        return cnt


class ContactCollector(BaseCollector):
    """
    联系人信息采集类
    """
    serializer_class = ContactSerializer

    def book_file(self):
        data_dir = account_dir_name(self.account)
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        return os.path.join(
            data_dir,
            contact_xlsx(self.account),
        )

    def page_detail(self, page_num, customer_id):
        """
        返回每页响应信息
        :return:
        """
        path = "/snucs/customer/contacts"
        json_data = {
            "param": {"sortKey": "watermark_alpha", "sortedColumn": "", "sortedType": "", "customerId": customer_id},
            "page": {"pageSize": self.page_size, "currentPage": page_num},
        }
        try:
            res = requests.post(f"{BASE_URL}{path}", headers=HEADERS, json=json_data, cookies=self.auth_cookie,
                                verify=False)
            assert res.status_code == 200, res.status_code
            data = res.json()
            logger.info(data)
        except Exception as e:
            logger.exception(e)
        else:
            if data.get("ret") == "0000":
                return data.get("data")
        return {}

    def collect(self):
        cnt = 0
        if not self.auth_cookie:
            return cnt
        tasks = self.session.query(Task).filter_by(account=self.account).all()
        ids = [int(task.customer_id) for task in tasks]
        for customer_id in ids:
            data = self.page_detail(1, customer_id)
            # page = {
            #     "count": 388,  # 总数量
            #     "currentPage": 2,  # 当前页码
            #     "index": 10,  # 最后一条的索引？
            #     "pageSize": 10,  # 每页条数
            #     "pages": 39,  # 总页数
            # }
            # 查询所有页
            if not data:
                continue
            pages = int(data.get("page", {}).get("pages", 1))
            for p in range(1, pages + 1):
                per_page = self.page_detail(p, customer_id)
                _list = per_page.get("list", [])
                for detail in _list:
                    """
                    bankCustNum: null
                    certNo: "140224199010070015"
                    certType: "1011"
                    connRate: 384
                    contactName: "代玉红"
                    contactNo: "13546005030"
                    contactRel: "99"
                    contactSrc: "1001"
                    customerId: 1136593
                    dCreateTime: 1567692590000
                    dCreateUserId: "CCMS_DATA_CUST_CONT"
                    dUpdateTime: 1592384247000
                    dUpdateUserId: "system"
                    discarded: false
                    discardedTime: null
                    id: 255149110
                    invalidTelCount: 0
                    lastTelRes: "0006"
                    reachCount: 0
                    remark: null
                    status: null
                    telCount: 56
                    toTop: false
                    toTopTime: null
                    validTelCount: 3
                    version: 1
                    """
                    d = dict(
                        account=self.account,
                        contact_id=detail.get("id", NA),
                        customer_id=detail.get("customerId", NA),
                        contact_name=detail.get("contactName", NA),
                        id_num=detail.get("certNo", NA),
                        phone=detail.get("contactNo", NA),
                        relationship=self.relationship_by_code(detail.get("contactRel", NA)),
                    )
                    self.session.add(Contact(**d))
                    self.session.flush()
                    cnt += 1
                    console(f"获取到用户信息: {d['contact_name']}-{d['phone']}")
                time.sleep(self.sleep)
        return cnt

    def relationship_by_code(self, code):
        """
        获取联系人关系: 此处发现没有发送任何而请求，最后在js文件中发现是前端枚举
        :param code:
        :return:
        """
        relations = {
            "00": "配偶",
            "01": "亲属",
            "02": "朋友",
            "03": "同事",
            "04": "父母",
            "05": "子女",
            "06": "兄弟姐妹",
            "07": "其他",
            "08": "无关人员",
            "99": "本人",
        }

        return relations.get(code, NA)
