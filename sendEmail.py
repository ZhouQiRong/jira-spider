import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import encoders
from email.utils import parseaddr, formataddr
from threading import Thread
import time
import  os


class sendEmail(Thread):
    def __init__(self, year,month):
        super().__init__()
        self.year = year
        self.month = month

    def run(self):
        time.sleep(3)
        if (os.path.isfile('D:\\pythonNotebook\jira\jira\saveExcel\Jira{0}{1}Report.xls'.format(self.year, self.month))):
            fileName = 'D:\\pythonNotebook\jira\jira\saveExcel\Jira{0}{1}Report.xls'.format(self.year,self.month)
            print("汇总统计文件{0}已存在，开始发送邮件...".format(fileName))
            self.send()

    def send(self):
        print("5.开始发送汇总统计Excel文件...")
        msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
        # 输入Email地址和口令:
        from_addr = "zhouqirong@lifeisgreat.com.cn"
        password = "Zqr,123456"
        # 输入SMTP服务器地址:
        smtp_server = "smtp.lifeisgreat.com.cn"
        # 输入收件人地址:
        to_addr = "zhouqirong@lifeisgreat.com.cn"
        msg = MIMEMultipart()
        msg['From'] = self.emailFormatAddr(u'周启荣<%s>' % from_addr)
        msg['To'] = self.emailFormatAddr(u'岳金伟<%s>' % to_addr)
        msg['Subject'] = Header(u'Jira{0}年{1}月任务量统计'.format(self.year, self.month), 'utf-8').encode()

        # 邮件正文内容
        msg.attach(MIMEText('这是{0}年{1}月Jira任务数据统计信息，详情参见附件！'.format(self.year, self.month), 'plain', 'utf-8'))
        # 构造附件1，传送当前目录下的 test.txt 文件
        att1 = MIMEText(open('D:\\pythonNotebook\jira\jira\saveExcel\Jira{0}{1}Report.xls'.format(self.year,self.month), 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att1["Content-Disposition"] = 'attachment; filename='+"Jira{0}{1}Report.xls".format(self.year,self.month)
        msg.attach(att1)

        server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
        #server.set_debuglevel(1)  #是否开启调试模式,查看后台打印信息
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
        print("......邮件发送完成......")

    def emailFormatAddr(self,s):
        name, addr = parseaddr(s)
        return formataddr(( Header(name, 'utf-8').encode(), addr))