
#!/usr/bin/env python  
# -*- coding:utf-8 -*-  
"""
@desc: flask_sqlalchemy 拓展
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
