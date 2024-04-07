#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@desc: flask_migrate 拓展
"""
import flask_migrate


def init(app, db):
    flask_migrate.Migrate(app, db)