import scrapy
from scrapy.selector import Selector
from scrapy.http import Request , FormRequest
import  json
from scrapy.utils.project import get_project_settings
from jira.items import Summary
from .DateUtil import DateUtil
from .sendEmail import sendEmail
from datetime import datetime

#爬虫启动
#1.cmd 进入路径:    D:\pythonNotebook\jira\jira\spiders
#2.运行脚本：    scrapy crawl jira

class JiraSpider(scrapy.Spider):
    # 指定唯一爬虫名
    name = "jira"

    # 设置允许访问Jira域名
    allowed_domain = "http://jira.XXXX.com.cn"

    # 设置Jira初始访问页面
    start_urls = [
        "http://jira.XXXX.com.cn/secure/Dashboard.jspa"
    ]

    # 设置浏览器用户代理
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    header_nocheck = {
        'X-Atlassian-Token': 'nocheck'
    }

    #初始化查询起始日期，项目、查询类型及生产问题原因等需要用到的变量
    def __init__(self):
        print("JiraSpider init starting...")
        self.startDate = datetime(2018,7,1)
        self.endDate = datetime(2018,7,26)
        self.projects = None
        self.tpwcases = None
        self.summaryDict = {}
        self.productionDict = {}
        # 获取所有配置参数
        self.settingsDict = self.getSettings()
        print("JiraSpider inited...")

    def getSettings(self):

        settings = get_project_settings()
        '''
        #获取查询设置 年\月
        timeLimitDict = settings.get('TIMELIMIT')
        self.year = input("请输入年:")
        print("你输入的年是:%s"% self.year)
        self.month = input("请输入月份:")
        if(len(self.month) < 2):
            self.month = '0'+ self.month
        print("你输入的月份是:%s" % self.month)


        dateUtil = DateUtil()
        #根据年月获取该月初始日期和终止日期
        self.startDate, self.endDate = dateUtil.getMonthFirstDayAndLastDay(self.year, self.month)
        '''
        print("get startDate is : {0} endDate is : {1}".format(self.startDate,self.endDate))
        settingsDict = {}
        self.projects = settings.get('PROJECT')
        tmps = settings.get('TMP')
        settingsDict['TMP'] = tmps
        sops = settings.get('SOP')
        settingsDict['SOP'] = sops
        tpws = settings.get('TPW')
        settingsDict['TPW'] = tpws
        self.tpwcases = settings.get('TPWCASE')
        return settingsDict

    def start_requests(self):
        print("1.开始请求JIRA登录页面...")
        yield Request("http://jira.XXXX.com.cn/login.jsp",meta={'cookiejar':1}, callback=self.login)

        #print('主进程启动发送邮件线程开始...')
        #t = sendEmail(self.year,self.month)
        #t.start()
        print('主进程结束！！！')



    def login(self, response):
        print("2.提交用户名密码登录Jira账户...")
        #设置登录用户密码，登录JIRA
        return [FormRequest.from_response(response,
                                          "http://jira.XXXX.com.cn/login.jsp",
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          headers=self.header,
                                          formdata={'os_username': 'username',
                                                    'os_password': 'password',###################################注意更改密码
                                                    'os_destination': '',
                                                    'user_role': '',
                                                    'atl_token': '',
                                                    'login': '登录'
                                                    },
                                          callback=self.go_my_filter_page
                                          )]

    def go_my_filter_page(self, response):
        print("3.登录我收藏的过滤器，月度任务统计...")
        #设置登陆后跳转至个人收藏的过滤器，过滤器（filter = 10961）月度任务统计,
        return [Request("http://jira.XXXX.com.cn/issues/?filter=10961", meta={'cookiejar': 1},
                        callback=self.my_filter_count)]

    #组装参数查询项目类型任务数
    def my_filter_count(self, response):
        print("4.返回我的收藏过滤器页面，并返回默认初始页面信息...")

        #TODO
        #projects = response.xpath('//div[@id="criteriaJson"]/text()').extract()
        #values_m = ''.join(projects).split('values":')[1:]
        #values = ''.join(values_m)[:-1]
        #ret_html = response.body.decode(response.encoding)
        #filter_html = open('E:\\filter_10961.html', 'w')
        #filter_html.write(ret_html)

        #统计各项目类型，查询类型任务总数
        for key,values in self.settingsDict.items():
            for value in values:
                case = ""
                jql = "project = " + key + " AND issuetype = " + value + " AND created >= " + self.startDate.strftime(
                            '%Y-%m-%d') + " AND created <=" + self.endDate.strftime('%Y-%m-%d')
                yield FormRequest(
                    url="http://jira.XXXX.com.cn/rest/issueNav/1/issueTable",
                    headers=self.header_nocheck,
                    meta={'cookiejar': response.meta['cookiejar'], 'project': key, 'issuetype': value, 'case': case,
                          'startDate': self.startDate.strftime('%Y-%m-%d'),
                          'endDate': self.endDate.strftime('%Y-%m-%d')},
                    dont_filter=True,
                    formdata={'startIndex': '0',
                              'filterId': '10961',
                              'dont_filter': 'True',
                              'jql': jql,
                              'layoutKey': 'list-view'
                              },
                    callback=self.prase
                )
        #统计生产问题具体原因数量
        for case in self.tpwcases:
             jql = "project = " + key + " AND issuetype = " + value + " AND 问题原因 = " + case + " AND created >= " + self.startDate.strftime(
                 '%Y-%m-%d') + " AND created <=" + self.endDate.strftime('%Y-%m-%d')
             yield FormRequest(
                 url="http://jira.XXXX.com.cn/rest/issueNav/1/issueTable",
                 headers=self.header_nocheck,
                 meta={'cookiejar': response.meta['cookiejar'], 'project': key, 'issuetype': value, 'case': case,
                       'startDate': self.startDate.strftime('%Y-%m-%d'), 'endDate': self.endDate.strftime('%Y-%m-%d')},
                 dont_filter=True,
                 formdata={'startIndex': '0',
                           'filterId': '10961',
                           'dont_filter': 'True',
                           'jql': jql,
                           'layoutKey': 'list-view'
                           },
                 callback=self.prase
             )

        # time.sleep(10)
        # self.sendEmail()

    #过滤器应用1请求后返回数据Json串处理
    def prase(self,response):
        #类似用法：response.body.decode(response.encoding)
        ret_json = json.loads(response.body_as_unicode())
        item =  Summary()
        item['startDate'] =  response.meta['startDate']
        item['endDate'] = response.meta['endDate']
        item['project'] = response.meta['project']
        item['issuetype'] = response.meta['issuetype']
        item['case'] = response.meta['case']
        item['total'] = ret_json['issueTable']['total']

        if item['project'] == "TPW":
            print('项目类型 : {0} 问题类型  : {1}  问题原因: {2}  任务总数是 is : {3}'.format(item['project'], item['issuetype'],item['case'], item['total']))
        else:
            print('项目类型 : {0} 问题类型  : {1}  任务总数是 is : {2}'.format(item['project'], item['issuetype'],item['total']))
        return item
