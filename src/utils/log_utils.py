#!/usr/bin/env python
# -*- coding:utf-8 -*-

import typing as t
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from common.config import config
from common import const

root_path: Path = const.ROOT_PATH
logger_dir_name = config.LOG_DIR
logdir = root_path.joinpath(logger_dir_name)  # 项目日志目录
os.makedirs(logdir, exist_ok=True)


def get_log_formatter():
    return logging.Formatter('%(asctime)s %(levelname)s %(name)s [pid:%(process)d] [tid:%(thread)d] '
                             '[%(filename)s.py %(lineno)d %(funcName)s] %(message)s')


def create_console_handler(level=logging.DEBUG):
    """创建控制台日志handler

    Args:
        level: 级别

    Returns: StreamHandler

    """
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = get_log_formatter()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    return console_handler


def create_file_handler(filename: t.Union[str, Path], level=logging.DEBUG):
    """创建文件日志handler

    Args:
        filename: 文件路径
        level: 日志级别

    Returns: TimedRotatingFileHandler

    """

    file_handler = TimedRotatingFileHandler(
        filename,
        when=config.LOG_WHEN,
        interval=config.LOG_INTERVAL,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    formatter = get_log_formatter()
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    return file_handler


def init_logger(logger_name: str, filename: t.Union[str, Path] = None, save_level: bool = False):
    """初始化logger

    Args:
        logger_name(str): logger 名称
        filename(str|Path): logger写入文件的路径
        save_level(bool): 是否将对应级别以上的日志写入对应的文件，默认为False

    Returns:

    """
    if filename is None:
        filename = logdir.joinpath(f"{logger_name}.log")
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # 设置控制台日志
    config_level = config.LOG_LEVEL
    console_handler = create_console_handler(level=config_level)
    logger.addHandler(console_handler)

    # 设置日志文件
    default_file_handler = create_file_handler(filename, level=config_level)
    logger.addHandler(default_file_handler)

    if save_level:
        # 将对应级别以上的日志写入对应的文件
        # 如：DEBUG级别以上的写入debug.log
        log_levels = {
            logging.DEBUG: "debug.log",
            logging.INFO: "info.log",
            logging.WARNING: "warning.log",
            logging.ERROR: "error.log"
        }
        for level, log_file_name in log_levels.items():
            log_file = logdir.joinpath(log_file_name)
            log_level_file_handler = create_file_handler(log_file, level)
            logger.addHandler(log_level_file_handler)

    return logger


def init_loggers():
    logger_names = [
        "run",
        "api",
        "params",
        "core",
        "service",
        "task",
        "test"
    ]
    for logger_name in logger_names:
        init_logger(logger_name, save_level=True)
