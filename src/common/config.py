#!/usr/bin/env python  
# -*- coding:utf-8 -*-  
import logging
import os

import dotenv

logger = logging.getLogger("run")

dotenv.load_dotenv()

# 默认配置 如果env文件中不存在则使用默认配置
DEFAULTS = {
}


def get_env(key):
    return os.environ.get(key, DEFAULTS.get(key))


def get_bool_env(key):
    value = get_env(key)
    return value.lower() == "true" if value is not None else False


def get_cors_allow_origins(env, default):
    cors_allow_origins = []
    if get_env(env):
        for origin in get_env(env).split(","):
            cors_allow_origins.append(origin)
    else:
        cors_allow_origins = [default]

    return cors_allow_origins


class Config:
    """Application configuration class."""

    def __init__(self):
        # ------------------------
        # 常规配置
        # ------------------------

        # 密钥将用于对会话 cookie 进行安全签名
        # 可以使用 "openssl rand -base64 42" 生成强密钥。
        # 或者用 "SECRET_KEY" 环境变量来设置它。
        self.SECRET_KEY = get_env("SECRET_KEY")

        # 跨域设置 settings
        self.API_CORS_ALLOW_ORIGINS = get_cors_allow_origins("API_CORS_ALLOW_ORIGINS", "*")

        # ------------------------
        # 数据库配置
        # ------------------------
        self.DB_USERNAME = get_env("DB_USERNAME")
        self.DB_PASSWD = get_env("DB_PASSWORD")
        self.DB_HOST = get_env("DB_HOST")
        self.DB_PORT = get_env("DB_PORT")
        self.DB_NAME = get_env("DB_DATABASE")
        self.DB_CHARSET = get_env("DB_CHARSET")
        self.DB_EXTRAS = f"?client_encoding={self.DB_CHARSET}" if self.DB_CHARSET else ""
        self.SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{self.DB_USERNAME}:{self.DB_PASSWD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}{self.DB_EXTRAS}"
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(get_env("SQLALCHEMY_POOL_SIZE")),
            "pool_recycle": int(get_env("SQLALCHEMY_POOL_RECYCLE"))
        }
        self.SQLALCHEMY_ECHO = get_bool_env("SQLALCHEMY_ECHO")

        # ------------------------
        # Redis配置
        # ------------------------
        self.REDIS_HOST = get_env("REDIS_HOST")
        self.REDIS_PORT = int(get_env("REDIS_PORT"))
        self.REDIS_USERNAME = get_env("REDIS_USERNAME")
        self.REDIS_PASSWORD = get_env("REDIS_PASSWORD")
        self.REDIS_DB = get_env("REDIS_DB")
        self.REDIS_NAMESPACE = get_env("REDIS_NAMESPACE")

        # ------------------------
        # Celery配置
        # ------------------------
        self.CELERY_BROKER_URL = get_env("CELERY_BROKER_URL")
        self.CELERY_BACKEND = get_env("CELERY_BACKEND")
        self.CELERY_RESULT_BACKEND = self.CELERY_BROKER_URL
        self.BROKER_USE_SSL = self.CELERY_BROKER_URL.startswith("rediss://")

        # ------------------------
        # 文件存储配置 默认使用本地存储
        # ------------------------
        self.STORAGE_TYPE = get_env("STORAGE_TYPE")
        self.STORAGE_LOCAL_PATH = get_env("STORAGE_LOCAL_PATH")
        self.SOTRAGE_ENTPOINT = get_env("SOTRAGE_ENTPOINT")
        self.STORAGE_BUCKET = get_env("STORAGE_BUCKET")
        self.STORAGE_ACCESS_KEY = get_env("STORAGE_ACCESS_KEY")
        self.STORAGE_SECRET_KEY = get_env("STORAGE_SECRET_KEY")
        self.STORAGE_SECURE = get_bool_env("STORAGE_SECURE")

        # ------------------------
        # 日志配置
        # ------------------------
        self.LOG_LEVEL = get_env("LOG_LEVEL")
        self.LOG_DIR = get_env("LOG_DIR")
        self.LOG_WHEN = get_env("LOG_WHEN")
        self.LOG_INTERVAL = int(get_env("LOG_INTERVAL"))
        self.LOG_BACKUP_COUNT = int(get_env("LOG_BACKUP_COUNT"))


config = Config()
