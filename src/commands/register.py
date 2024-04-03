#!/usr/bin/env python  
# -*- coding:utf-8 -*-  


from commands.create_admin import create_admin_cmd


def register_commands(app):
    app.cli.add_command(create_admin_cmd)

