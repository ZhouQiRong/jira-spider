import calendar
import datetime


class DateUtil :

    def __init__(self):
        print("DateUtil init...")

    def getMonthFirstDayAndLastDay(self,year=None, month=None):
        """
        :param year: 年份，默认是本年，可传int或str类型
        :param month: 月份，默认是本月，可传int或str类型
        :return: firstDay: 当月的第一天，datetime.date类型
                  lastDay: 当月的最后一天，datetime.date类型
        """
        if year:
            year = int(year)
        else:
            year = datetime.date.today().year

        if month:
            month = int(month)
        else:
            month = datetime.date.today().month

        # 获取当月第一天的星期和当月的总天数
        firstDayWeekDay, monthRange = calendar.monthrange(year, month)

        # 获取当月的第一天
        firstDay = datetime.date(year=year, month=month, day=1)
        lastDay = datetime.date(year=year, month=month, day=monthRange)

        return firstDay, lastDay

if __name__=="__main__":
    dateUtil =  DateUtil()
    year = 2018
    month = 4
    a, b = dateUtil.getMonthFirstDayAndLastDay(year,month)
    print(a,b)