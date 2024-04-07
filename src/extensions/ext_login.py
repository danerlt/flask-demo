#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@desc: flask_login 拓展
"""
import flask_login

login_manager = flask_login.LoginManager()


def init_app(app):
    login_manager.init_app(app)
