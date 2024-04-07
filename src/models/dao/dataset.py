#!/usr/bin/env python  
# -*- coding:utf-8 -*-  

import datetime
from typing import Optional, Dict, List
from extensions.ext_db import db
from models.dataset import Dataset


class DatasetDao(object):

    @classmethod
    def create_dataset(cls, account_id: str = "", name: str = "", description: str = "",
                       configs: Optional[Dict] = None) -> Dataset:
        """创建数据集

        Args:
            account_id (str): 数据集ID
            name (str): 数据集名称
            description (str): 数据集描述
            configs: 数据集配置

        Returns: Dataset对象

        """
        if configs is None:
            # 如果configs为空，使用默认配置
            default_dataset_configs = Dataset.get_default_dataset_configs()
            configs = default_dataset_configs.to_dict()
        dataset = Dataset(account_id=account_id, name=name, description=description, configs=configs)
        db.session.add(dataset)
        db.session.commit()
        return dataset

    @classmethod
    def get_dataset(cls, dataset_id: Optional[str] = None, account_id: Optional[str] = None,
                    name: Optional[str] = None, deleted: bool = False) -> Dataset:
        """获取数据集

        Args:
            dataset_id (str): 数据集ID
            account_id (str): 用户ID
            name (str): 数据集名称
            deleted (bool): 是否删除 默认为False

        Returns: Dataset对象

        """
        query = db.session.query(Dataset)
        if dataset_id:
            query = query.filter(Dataset.id == dataset_id)
        if account_id:
            query = query.filter(Dataset.account_id == account_id)
        if name:
            query = query.filter(Dataset.name == name)
        query = query.filter(Dataset.deleted == deleted)
        dataset = query.first()
        return dataset

    @classmethod
    def dataset_is_exists(cls, dataset_id: Optional[str] = None, account_id: Optional[str] = None,
                          name: Optional[str] = None, deleted: bool = False) -> bool:
        """判断数据集是否存在

        Args:
            dataset_id (str): 数据集ID
            account_id (str): 用户ID
            name (str): 数据集名称
            deleted (bool): 是否删除 默认为False

        Returns: True or False, True: 数据集存在，False：数据集不存在

        """
        dataset = cls.get_dataset(dataset_id=dataset_id, account_id=account_id, name=name, deleted=deleted)
        if dataset:
            return True
        else:
            return False

    @classmethod
    def get_all_dataset(cls, account_id: Optional[str] = None, deleted: bool = False) -> List[Dataset]:
        """获取所有数据集

        Args:
            account_id (str): 用户ID
            deleted (bool): 是否删除 默认为False

        Returns: Dataset列表
        """
        query = db.session.query(Dataset)
        if account_id:
            query = query.filter(Dataset.account_id == account_id)
        query = query.filter(Dataset.deleted == deleted)
        dataset_list = query.all()
        return dataset_list

    @classmethod
    def update_dataset(cls, dataset: Dataset, name: Optional[str] = None, description: Optional[str] = None,
                       configs: Optional[Dict] = None) -> Dataset:
        """更新数据集

        Args:
            dataset:  数据集对象
            name (str): 数据集名称
            description (str): 数据集描述
            configs (dict): 数据集配置 如果为None则使用默认的配置

        Returns: Dataset对象

        """
        if name is not None:
            dataset.name = name
        if description is not None:
            # 更新数据集描述 可以设置成空字符串
            dataset.description = description
        if configs is not None:
            dataset.configs = configs
        elif dataset.configs is None:
            default_configs = dataset.get_default_dataset_configs()
            # 注意：default_configs 是一个对象，需要转换成字典
            dataset.configs = default_configs.to_dict()

        dataset.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        return dataset
