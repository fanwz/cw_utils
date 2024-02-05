import datetime
import time
import re


def day_delta(date, ddays):
    dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    out_date = (dt + datetime.timedelta(days=ddays)).strftime("%Y-%m-%d")
    return out_date


def get_tradingday():
    dt_str = time.strftime("%Y-%m-%d %H%M%S-%u", time.localtime())
    dt_d = dt_str.split(" ")
    # nowdate = int(dt_d[0].replace("-", ""))
    nowdate = dt_d[0]
    localtime_w = dt_d[1]
    nowtime = int(localtime_w.split("-")[0])
    week = int(localtime_w.split("-")[1])
    # print(dt_str, nowdate, localtime_w, nowtime, week)

    if nowtime < 23000:
        if week == 6:
            td_day = day_delta(nowdate, 2)
        elif week == 7:
            td_day = day_delta(nowdate, 1)
        else:
            td_day = day_delta(nowdate, 0)
    elif nowtime < 153000:
        td_day = nowdate
    else:
        if week == 5:
            td_day = day_delta(nowdate, 3)
        else:
            td_day = day_delta(nowdate, 1)

    return int(td_day.replace("-", ""))


def get_tradingday_new():
    from datetime import datetime, timedelta
    # 获取当前时间和星期
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    day_of_week = now.isoweekday()  # 1=Monday, 7=Sunday

    # 定义函数，用于格式化日期为YYYYMMDD格式
    def format_date(date): return date.strftime('%Y%m%d')

    if hour < 2 or (hour == 2 and minute < 30):
        # 当前时间小于2:30
        if day_of_week in [6, 7]:  # Saturday or Sunday
            # 下周一
            return format_date(now + timedelta(days=(8 - day_of_week)))
        else:
            # 当天
            return format_date(now)
    elif hour < 20:
        # 当前时间大于2:30且小于20:00，交易日是当天
        return format_date(now)
    else:
        # 当前时间大于20:00
        if day_of_week in [5, 6, 7]:  # Friday, Saturday, or Sunday
            # 下周一
            return format_date(now + timedelta(days=(8 - day_of_week)))
        else:
            # 第二天
            return format_date(now + timedelta(days=1))


def get_inst_info(inst):
    reg = r'^([A-Za-z]{1,2})(\d{3,4})$'
    m = re.match(reg, inst)
    if m:
        prd = m.group(1)
        endmon = m.group(2)
    else:
        return (None, None)
    # print(prd, endmon)
    # print(m.group(0))
    return (prd, endmon)


def get_day_night_period():
    '''
    night:>20:00:00 or < 2:30:00
    '''
    nt = int(time.strftime("%H%M%S", time.localtime()))
    if nt > 200000 or nt < 23000:
        return "night"
    else:
        return "day"


def check_new_tradingday(checkday):
    if get_tradingday() > checkday:
        return True
    else:
        return False


if __name__ == "__main__":
    print(get_tradingday())
