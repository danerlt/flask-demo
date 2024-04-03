#!/usr/bin/env python  
# -*- coding:utf-8 -*-  

import typing as t
from enum import Enum


class Register(object):
    def __init__(self):
        self._register = {}

    def register(self, name: str, obj: t.Any):
        self.__setitem__(name, obj)

    def register_by_type(self, reg_type: Enum, obj: t.Any):
        name = reg_type.value
        self.register(name, obj)

    def get(self, name: str):
        return self.__getitem__(name)

    def get_alls(self) -> t.Dict:
        return self._register

    def get_all_names(self) -> t.List:
        return list(self._register.keys())

    def remove(self, name: str):
        self.__delitem__(name)

    def clear(self):
        self._register = {}

    # 下面是实现支持字典的语法
    def __getitem__(self, key):
        return self._register[key]

    def __setitem__(self, key, value):
        self._register[key] = value

    def __delitem__(self, key):
        del self._register[key]

    def __contains__(self, key):
        return key in self._register

    def __len__(self):
        return len(self._register)
