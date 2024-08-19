#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/26 16:32
# @Author  : AMR
# @File    : config_mod.py
# @Software: PyCharm

import io
import json
import sys
import collections


def py2_jsondump(data, filename, order=True):
    with io.open(filename, 'w', encoding='utf-8') as f:
        # keep original order
        if order:
            f.write(json.dumps(data, f, ensure_ascii=False, indent=2))
        else:
            f.write(json.dumps(data, f, ensure_ascii=False,
                    sort_keys=True, indent=2))


def py3_jsondump(data, filename, order=True):
    with io.open(filename, 'w', encoding='utf-8') as f:
        # keep original order
        if order:
            return json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            return json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=2)


def jsonload(filename, order=True):
    with io.open(filename, 'r', encoding='utf-8') as f:
        # read keey by original order
        if order:
            return json.load(f, object_pairs_hook=collections.OrderedDict)
        else:
            return json.load(f)


if sys.version_info[0] == 2:
    jsondump = py2_jsondump
elif sys.version_info[0] == 3:
    jsondump = py3_jsondump


def loadconfig(config):
    try:
        conf = jsonload(config)
        return conf
    except Exception as e:
        print(e)
        return {}


def saveconfig(config, path):
    jsondump(config, path)


class JsonMod(object):
    def __init__(self, conf_file):
        self.conf_file = conf_file
        self.conf_data = loadconfig(conf_file)

    def __location(self, loc):
        curr_level = self.conf_data
        for key in loc:
            # print(key)

            # the root loc
            if key == "":
                break

            if key in curr_level:
                curr_level = curr_level[key]
            else:
                print("[Error]location fail.the key({}) not in data!".format(key))
                return None
        return curr_level

    def save_conf(self):
        saveconfig(self.conf_data, self.conf_file)

    def move_json_key_value(self, loc, move_key, move_index, save=True):
        curr_level = self.__location(loc)
        if curr_level is None:
            return

        data = curr_level

        if move_key not in data:
            # 如果move_key在JSON文件中不存在，则不进行任何操作
            return self.conf_data

        # 将 move_key 对应的键值对从原来的位置删除
        move_value = data.pop(move_key)

        # 将 move_key 对应的键值对插入到指定位置
        data_list = list(data.items())
        data_list.insert(move_index, (move_key, move_value))

        # new_data = collections.OrderedDict(data_list)
        # # update do not keep the new dict order
        # data.update(new_data)

        # 在传入的 json_data 中直接更新键值顺序
        for index, (key, value) in enumerate(data_list):
            if index == move_index:
                data[move_key] = move_value
            else:
                old_key, old_value = data.popitem(last=False)
                data[old_key] = old_value

        # print(data)
        if save:
            self.save_conf()

    # loc:the location of target para.use list for store one by one level.
    # new_kv:new key-value pair.use object
    def add_new_para(self, loc, new_kv, save=True):
        curr_level = self.__location(loc)
        if curr_level is None:
            return

        key = list(new_kv.keys())[0]
        value = new_kv[key]
        # print(key, value)
        curr_level[key] = value
        # print(self.conf_data)

        if save:
            self.save_conf()

    # loc:the location of target para.use list for store one by one level.
    # kv:key-value pair.use object. must check the key is exist!
    def change_value(self, loc, kv, save=True):
        curr_level = self.__location(loc)
        if curr_level is None:
            return

        key = list(kv.keys())[0]
        value = kv[key]

        if key not in curr_level:
            print("[Warning]the key({}) not in loc data,change value fail".format(key))
            return
        curr_level[key] = value

        if save:
            self.save_conf()

    # loc:the location of target para.use list for store one by one level.
    # key:the key need to get value
    def get_value(self, loc, key):
        curr_level = self.__location(loc)
        if curr_level is None:
            return None

        if key not in curr_level:
            print("[Warning]the key({}) not in loc data,get value fail".format(key))
            return None

        return curr_level[key]

    # loc:the location of target para.use list for store one by one level.
    # key:target key string
    def del_para(self, loc, key):
        curr_level = self.__location(loc)
        if curr_level is None:
            return

        if key not in curr_level:
            print("[Warning]the key({}) not in loc data,delete fail".format(key))
            return

        del curr_level[key]
        self.save_conf()

    # 新增的获取字段索引位置的函数
    def get_field_index(self, loc, target_field):
        curr_level = self.__location(loc)
        if curr_level is None:
            return None

        if isinstance(curr_level, dict):
            keys = list(curr_level.keys())
            if target_field in keys:
                return keys.index(target_field)
            else:
                print("[Warning]the field({}) not found in the specified location".format(
                    target_field))
                return None
        else:
            print("[Error]the specified location does not contain a dictionary")
            return None

    def insert_fields(self, loc, new_fields, ref_field=None, before=True, save=True):
        """
        在指定 loc 下的 ref_field 字段位置前或后插入新的字段。

        参数:
        - loc: 用于定位插入位置的路径，是一个列表。
        - new_fields: 新插入的字段，可以是一个字典，包含一个或多个 key-value 对。
        - ref_field: 参考字段，指定在哪个字段的位置前或后插入新字段。如果不指定，则插入到 loc 下最后。
        - before: 布尔值，决定新字段插入在 ref_field 的前（True）或后（False）。默认为 True。
        - save: 布尔值，是否在操作后保存配置文件。默认为 True。
        """
        curr_level = self.__location(loc)
        if curr_level is None:
            return

        if not isinstance(curr_level, dict):
            print("[Error]The specified location does not contain a dictionary")
            return

        data_list = list(curr_level.items())

        # 如果 ref_field 不为空，找到它的位置
        if ref_field:
            try:
                ref_index = [key for key, _ in data_list].index(ref_field)
                # 调整插入位置
                insert_index = ref_index if before else ref_index + 1
            except ValueError:
                print("[Warning]The ref_field ({}) not found, appending to the end".format(
                    ref_field))
                insert_index = len(data_list)  # 如果找不到字段，则插入到最后
        else:
            insert_index = len(data_list)  # 如果没有指定 ref_field，则插入到最后

        # 将 new_fields 插入到指定位置
        for key, value in new_fields.items():
            data_list.insert(insert_index, (key, value))
            insert_index += 1  # 每次插入后索引加一

        # 更新字典
        curr_level.clear()
        curr_level.update(data_list)

        if save:
            self.save_conf()


if __name__ == "__main__":
    cm = JsonMod("test.json")
    print(cm.conf_data)
    cm.add_new_para(["node"], {"newpara": "newvalue"})
    cm.add_new_para(["info"], {"newpara1": 111})
    cm.add_new_para(["node"], {"newpara121": [1, 2]})
    cm.change_value(["node"], {"newpara121": "6666"})
    print(cm.get_value(["node"], "old_para"))
    print(cm.get_field_index(["info"], "newpara1"))
    # cm.del_para(["node"], "newpara121")
    
    cm.insert_fields(["node"], {"insertnew": "8888888","insertnew222": "2222"}, "inst", False)
