import time
import datetime
import psutil
import sys
import os
from traceback import TracebackException
import logging
import paramiko

ACTION_DATE = time.strftime("%Y-%m-%d", time.localtime())
ACTION_DATE_INT = int(time.strftime("%Y%m%d", time.localtime()))


def get_file_list(tg_dir):
    list = []
    for (dirpath, dirnames, filenames) in os.walk(tg_dir):
        list.extend(filenames)
        break
    list.sort()
    return list


def get_dir_list(tg_dir):
    list = []
    for (dirpath, dirnames, filenames) in os.walk(tg_dir):
        list.extend(dirnames)
        break
    list.sort()
    return list


def get_timestamp(fmt="%Y-%m-%d %H:%M:%S"):
    # return time.strftime(fmt, time.localtime())

    # 将时间戳转换为datetime对象
    dt_object = datetime.datetime.fromtimestamp(time.time())

    # 格式化日期和时间
    # 你可以根据需要更改格式字符串
    return dt_object.strftime(fmt)


def get_previous_day(date_str, date_format='%Y-%m-%d'):
    the_date = datetime.datetime.strptime(date_str, date_format)

    # 计算前一天的日期
    previous_day = the_date - datetime.timedelta(days=1)

    # 将结果转换回字符串格式
    return previous_day.strftime(date_format)


def timestr_to_unix_time(time_str, dt_format='%Y-%m-%d %H:%M:%S.%f', tz_str='UTC'):
    # 直接计算时区偏移
    offset = 0  # 默认为UTC，即偏移0小时
    if tz_str.startswith('UTC'):
        offset = int(tz_str[3:] or 0)  # 提取偏移小时数，如果没有指定则默认为0
    tz = datetime.timezone(datetime.timedelta(hours=offset))

    # 分割时间字符串以处理可能的毫秒
    try:
        # 如果格式中包含毫秒，直接解析
        dt = datetime.datetime.strptime(time_str, dt_format)
    except ValueError:
        # 如果没有毫秒或格式不匹配，尝试解析没有毫秒的部分
        dt = datetime.datetime.strptime(
            time_str.split('.')[0], dt_format.split('.')[0])
        if '.' in time_str:
            ms = int(time_str.split('.')[1])
            dt += datetime.timedelta(milliseconds=ms)

    # 应用时区
    dt = dt.replace(tzinfo=tz)

    # 转换为UTC时间并计算Unix时间戳
    return dt.astimezone(datetime.timezone.utc).timestamp()


def get_all_processes(filter_str, by="name"):
    process_list = []
    for proc in psutil.process_iter():
        # print(proc)
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
        except psutil.NoSuchProcess:
            pass
        else:
            # logging.debug(pinfo)
            # print(pinfo)
            if filter_str is not None:
                if by == "name":
                    if pinfo["name"].find(filter_str) == -1:
                        continue
                elif by == "cmdline":
                    if type(pinfo["cmdline"]) != list:
                        continue
                    if len(pinfo["cmdline"]) == 0:
                        continue
                    cmdline_str = " ".join(pinfo["cmdline"])
                    # print(cmdline_str)
                    if cmdline_str.find(filter_str) == -1:
                        continue

                elif by == "pid":
                    if filter_str != pinfo["pid"]:
                        continue
            process_list.append(pinfo)
    return process_list


def get_package_temp():
    temps = psutil.sensors_temperatures()
    if not temps:
        return None
    try:
        return temps['coretemp'][0].current
    except:
        return None


def get_disk_space(path) -> str:
    # get disk usage statistics
    disk = psutil.disk_usage(path)

    free_bytes = disk.free
    free_GB = disk.free // (2**30)

    return free_bytes


def is_number(s, isfloat=False):
    if isfloat:
        try:
            float(s)
            return True
        except ValueError:
            pass
    else:
        try:
            int(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

    return False


def get_exception_msg(etype, value, tb, limit=None, file=None, chain=True):
    # copy from def print_exception(etype, value, tb, limit=None, file=None, chain=True):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """
    # format_exception has ignored etype for some time, and code such as cgitb
    # passes in bogus values as a result. For compatibility with such code we
    # ignore it here (rather than in the new TracebackException API).

    msg = ""
    if file is None:
        file = sys.stderr
    for line in TracebackException(
            type(value), value, tb, limit=limit).format(chain=chain):
        # print(line, file=file, end="")
        msg += line

    return msg


class HtmlTableGenerator(object):
    style_bg_false = 'background:#ffcc00;'
    style_bg_abnormal = 'background:#ff1a1a;'

    def __init__(self, header: list) -> None:
        super().__init__()

        self.style_tb = 'font-family: verdana,arial,sans-serif;font-size:16px;color:#333333;border-width: 1px;border-collapse: collapse;'
        self.style_tb_tr = 'text-align:center;'
        self.style_tb_th = 'border-width: 1px;padding: 6px;border-style: solid;border-color: #999999;text-align:center;'
        self.style_tb_td = 'border-width: 1px;padding: 2px 6px 2px 6px;border-style: solid;border-color: #999999;font-size:16px;'

        self.col_len = len(header)

        # build header line with input header list
        header_line = '<th style="{th}">' + '''</th>
                        <th style="{th}">'''.join(header) + '</th>'

        # init html text front with header_line
        self.html_text = '''
        <table border="1" style="{tb}">
        <thead>
        <tr style="{tr}">
        {hl}
        </tr>
        </thead>
        <tbody>
        '''.format(tb=self.style_tb, tr=self.style_tb_tr, hl=header_line)

        # fill th with style
        self.html_text = self.html_text.format(th=self.style_tb_th)

    def add_one_line(self, line: list, last_line=False):
        if len(line) != self.col_len:
            print("line len is not match.input len is {},col len is {}",
                  len(line), self.col_len)
            return

        self.html_text += '<tr style="{st}">'.format(st=self.style_tb_tr)
        for i in range(len(line)):
            l = line[i]

            if i == 0:
                self.html_text += '<th style="{st}">{v}</th>'.format(
                    st=self.style_tb_th, v=l)
                continue

            style = self.style_tb_td
            if isinstance(line[i], tuple):
                d = l[0]
                style += " " + l[1]
            else:
                d = l

            self.html_text += '<td style="{st}">{v}</td>'.format(st=style, v=d)

        self.html_text += "</tr>"

        if last_line:
            self.html_text += '''  </tbody>
                    </table>
                '''

    def get_html_text(self):
        return self.html_text

    def show_html_text(self):
        print(self.html_text)


class HtmlTextGenerator(object):
    C_YELLOW = "color:#ffcc00;"
    C_GREEN = "color:#00ff00;"
    C_RED = "color:#E53333;"
    C_BLUE = "color:#0000ff;"

    def __init__(self) -> None:
        self.html_text = ""

    def get_color(msg, color: str):
        c = color.upper()
        if c == 'Y' or 'YELLOW':
            return HtmlTextGenerator.C_YELLOW
        elif c == 'R' or 'RED':
            return HtmlTextGenerator.C_RED
        elif c == 'G' or 'GREEN':
            return HtmlTextGenerator.C_GREEN
        elif c == 'B' or 'BLUE':
            return HtmlTextGenerator.C_BLUE

    def add_text(self, text, style=""):
        self.html_text += '<span style="{}">{}</span><br>\n'.format(
            style, text)

    def get_html_text(self):
        return self.html_text


def msg_color(msg, color="default", attr=1):
    '''
    attr:
    0 - 终止 attributive 属性
    1 - 开始 attributive 属性
    2 - 闪烁
    3 - 下划线
    4 - 粗体
    5 - 闪烁下划线
    7 - 反向
    8 - 隐体
    '''
    c = color.upper()
    if c == 'Y' or c == 'YELLOW':
        return '\033[{};33m{}\033[0m'.format(attr, msg)
    elif c == 'R' or c == 'RED':
        return '\033[{};31m{}\033[0m'.format(attr, msg)
    elif c == 'G' or c == 'GREEN':
        return '\033[{};32m{}\033[0m'.format(attr, msg)
    elif c == 'B' or c == 'BLUE':
        return '\033[{};34m{}\033[0m'.format(attr, msg)
    else:
        return msg


def parse_string_to_int_list(input_str):
    # code by chatgpt3.5
    '''
    prompt:解析字串转成int 型数组。支持多种类型的转换，例如"2-10" 这样形式的转换成[2,3,4,5,6,7,8,9,10]。如“1-2,5”则转换成[1,2,5]。如“3,5”，则转换成[3,5]。并且支持非法字符检查
    '''
    # 用于存储结果的列表
    result = []

    # 将输入字符串按逗号分隔成多个子字符串
    sub_strings = input_str.split(",")

    # 循环处理每个子字符串
    for sub_str in sub_strings:
        # 如果子字符串包含连字符，则将其视为范围
        if "-" in sub_str:
            range_parts = sub_str.split("-")
            # 确保分割后只有两个元素
            if len(range_parts) != 2:
                raise ValueError("Invalid range: {}".format(sub_str))

            # 将范围转换为整数
            start = int(range_parts[0])
            end = int(range_parts[1])

            # 确保范围有效
            if start >= end:
                raise ValueError("Invalid range: {}".format(sub_str))

            # 将范围内的整数添加到结果列表中
            for i in range(start, end+1):
                result.append(i)
        else:
            # 如果子字符串不包含连字符，则将其视为单个整数
            try:
                num = int(sub_str)
                result.append(num)
            except ValueError:
                raise ValueError("Invalid integer: {}".format(sub_str))

    return result


class RemoteHub(object):
    def __init__(self) -> None:
        super().__init__()

    def push(self, data):
        raise NotImplementedError


class RemoteServer(RemoteHub):
    '''
    "remote_hub" : {
      "Type" : "SSH",
      "IP" : "123.0.6.1",
      "Port" : "23333",
      "User" : "test",
      "Password" : "test",
      "recv_dir" : "/data/"
   }
    '''

    def __init__(self, remote_config) -> None:
        super().__init__()
        self.srv_type = remote_config["Type"]
        if self.srv_type.upper() == "SSH":
            self.ip = remote_config["IP"]
            self.port = remote_config["Port"]
            self.user = remote_config["User"]
            self.password = remote_config["Password"]
            if "RSAKey" in remote_config.keys():
                self.rsakey = remote_config["RSAKey"]
            else:
                self.rsakey = "~/.ssh/id_rsa"
            self.recv_dir = remote_config["recv_dir"]
        else:
            print("remote server type {} is not support!".format(self.srv_type))

    def push(self, data):
        if self.srv_type.upper() == "SSH":
            cmd = 'rsync -avzP --timeout=30 -e \'ssh -i {5} -p {0}\' {1} {4}@{2}:{3}'.format(self.port,
                                                                                             data, self.ip, self.recv_dir, self.user, self.rsakey)
            ret = os.system(cmd)
            if ret == 0:
                print("push file sucess")
            else:
                print("push file error.ret={}".format(ret))
        else:
            print("remote server type {} is not support!".format(self.srv_type))

    def execute_command(self, command):
        if self.srv_type.upper() == "SSH":
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                # 如果提供了RSA密钥，则使用密钥认证；否则使用密码认证
                if self.rsakey and os.path.exists(os.path.expanduser(self.rsakey)):
                    rsa_key = paramiko.RSAKey.from_private_key_file(
                        os.path.expanduser(self.rsakey))
                    client.connect(self.ip, port=self.port,
                                   username=self.user, pkey=rsa_key)
                else:
                    client.connect(self.ip, port=self.port,
                                   username=self.user, password=self.password)

                stdin, stdout, stderr = client.exec_command(command)
                output = stdout.read() + stderr.read()
                client.close()
                return output.decode('utf-8')
            except Exception as e:
                print(f"Failed to execute command: {e}")
        else:
            print("Remote server type {} is not supported for command execution.".format(
                self.srv_type))


def setup_logger(name, log_file, log_level=logging.INFO, log_format=None, date_format=None, console_logging=True):
    """
    创建并返回一个配置好的logger。

    :param name: logger的名称。
    :param log_file: 日志文件的路径。
    :param log_level: 日志级别，默认为 logging.INFO。
    :param log_format: 日志格式字符串。
    :param date_format: 日期格式字符串。
    :param console_logging: 是否在控制台也打印日志。
    :return: 配置好的logger。
    """
    # 如果日志文件目录不存在，创建它
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 如果未指定日志格式，使用默认格式
    if log_format is None:
        log_format = '%(asctime)s [%(levelname)s] at %(lineno)d: %(message)s'

    # 如果未指定日期格式，使用默认格式
    if date_format is None:
        date_format = '%Y-%m-%d(%a)%H:%M:%S'

    # 创建一个新的logger实例
    logger = logging.getLogger(name)

    if not logger.handlers:  # 检查是否已经添加了处理程序
        logger.setLevel(log_level)

        # 创建文件处理程序
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            log_format, datefmt=date_format))

        # 添加文件处理程序到logger
        logger.addHandler(file_handler)

        # 如果需要在控制台打印日志，添加一个 StreamHandler
        if console_logging:
            console = logging.StreamHandler()
            console.setLevel(log_level)
            console_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)-8s] %(message)s')
            console.setFormatter(console_formatter)
            logger.addHandler(console)

    return logger
