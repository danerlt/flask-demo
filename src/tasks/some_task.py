#!/usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@desc: 后台任务示例
"""
import logging
import typing as t

from celery import shared_task
from models.dao.dataset import DatasetDao
from models.dataset import Dataset, DatasetConfigs


logger = logging.getLogger("task")



@shared_task(queue='dataset')
def process_some_task(dataset_id: str):
    """处理xxx后台任务

    Args:
        dataset_id(str): 数据集ID 这里使用Dataset对象会导致Celery序列化失败
    
    Returns:

    """
    # 首先判断数据集是否存在
    dataset_id = str(dataset_id)
    dataset = DatasetDao.get_dataset(dataset_id=dataset_id)
    if dataset is None:
        logger.error(f"数据集不存在：数据集Id：{dataset_id}")
        return
    dataset_configs_dict = dataset.configs
    logger.info(f"{type(dataset_configs_dict)=}, {dataset_configs_dict=}")
    if dataset_configs_dict is None:
        logger.warning(f"数据集Id：{dataset_id}, configs为空，使用默认配置")
        dataset_configs = Dataset.get_default_dataset_configs()
    else:
        dataset_configs = DatasetConfigs.from_dict(dataset_configs_dict)

    # 下面是任务的实际逻辑
    pass