import time
import psutil
import sys
import os
from traceback import TracebackException

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


def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


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


def msg_color(msg, color: str):
    c = color.upper()
    if c == 'Y' or c == 'YELLOW':
        return '\033[1;33m{}\033[0m'.format(msg)
    elif c == 'R' or c == 'RED':
        return '\033[1;31m{}\033[0m'.format(msg)
    elif c == 'G' or c == 'GREEN':
        return '\033[1;32m{}\033[0m'.format(msg)
    elif c == 'B' or c == 'BLUE':
        return '\033[1;34m{}\033[0m'.format(msg)


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
            self.recv_dir = remote_config["recv_dir"]
        else:
            print("remote server type {} is not support!".format(self.srv_type))

    def push(self, data):
        if self.srv_type.upper() == "SSH":
            cmd = 'rsync -avzP -e \'ssh -p {0}\' {1} {2}:{3}'.format(self.port,
                                                                     data, self.ip, self.recv_dir)
            ret = os.system(cmd)
            if ret == 0:
                print("push file sucess")
            else:
                print("push file error.ret={}".format(ret))
        else:
            print("remote server type {} is not support!".format(self.srv_type))
