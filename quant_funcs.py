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


if __name__ == "__main__":
    print(get_tradingday())
