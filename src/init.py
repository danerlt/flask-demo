#!/usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@desc: 初始化脚本
"""
import subprocess
import sys

from sqlalchemy import create_engine, text

sys.path.append("/app/")

from common.config import config


def execute_cmd(cmd):
    print(f"start execute Command: {cmd}")
    # 注意，这个地方必须加上shell=True,否则会报错 `No Such File or Directory`
    p = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd="/app/", shell=True)
    stdout, stderr = p.communicate()
    return_code = p.returncode
    if return_code == 0:
        print(stdout.decode())
        print(f"Command '{cmd}' executed successfully")
    else:
        print(stderr.decode())
        print(f"Command '{cmd}' failed with exit code {return_code}")
        raise Exception(f"Command '{cmd}' failed with exit code {return_code}")


def database_is_exist():
    try:
        db_uri = config.SQLALCHEMY_DATABASE_URI
        engine = create_engine(db_uri)
        # 尝试连接到数据库
        with engine.connect() as connection:
            # 执行一个简单的无操作查询，比如查询版本信息或当前时间
            sql = text("SELECT 1")
            connection.execute(sql)
            # 如果能成功执行查询，说明数据库存在
            return True
    except Exception as e:
        print(f"判断数据库是否存在报错: {e}")
        # 捕获 OperationalError 异常，这类异常通常表示无法连接到数据库或数据库不存在
        if "not exist" in str(e):
            return False
        else:
            # 如果不是因为数据库不存在引发的异常，则重新抛出
            print(f"数据库错误: {e}")
            raise e


def create_database():
    print("create database")
    try:
        # 注意: sqlalchemy 2.0 和 psycopg2 默认情况执行创建数据库都会报错 `CREATE DATABASE cannot run inside a transaction block`
        # 需要手动设置隔离级别为 AUTOCOMMIT
        db_uri = f"postgresql+psycopg2://{config.DB_USERNAME}:{config.DB_PASSWD}@{config.DB_HOST}:{config.DB_PORT}/postgres"
        engine = create_engine(db_uri)
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            # 创建新数据库的 SQL 命令
            sql = text(f"CREATE DATABASE {config.DB_NAME} WITH OWNER = {config.DB_USERNAME} ENCODING = 'UTF8'")
            conn.execute(sql)
        print(f"create database: {config.DB_NAME} successfully")
    except Exception as e:
        print(f"创建数据库错误: {e}")
        raise e


def init_db():
    db_is_exist = database_is_exist()
    print(f"{db_is_exist=}")
    if not db_is_exist:
        print("database is not exist, need create it")
        # 创建数据库
        create_database()

        # 升级数据库
        cmd = "flask db upgrade"
        execute_cmd(cmd)
    else:
        # 升级数据库
        cmd = "flask db upgrade"
        execute_cmd(cmd)


def main():
    init_db()


if __name__ == '__main__':
    main()
