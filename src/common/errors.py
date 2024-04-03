#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging


class AppBaseException(Exception):

    def __init__(self, msg: str = None):
        self.msg = msg


class ParamsException(AppBaseException):

    def __init__(self, msg: str = None):
        super().__init__(msg=msg)
        self.log = logging.getLogger("params")
        self.log.error(msg)


class ApiException(AppBaseException):

    def __init__(self, msg: str = None):
        super().__init__(msg=msg)
        self.log = logging.getLogger("api")
        self.log.error(self.msg)


class ServiceError(AppBaseException):

    def __init__(self, msg: str = None):
        super().__init__(msg=msg)
        self.log = logging.getLogger("service")
        self.log.error(self.msg)

