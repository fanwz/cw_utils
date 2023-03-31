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
