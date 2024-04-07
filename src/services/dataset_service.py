#!/usr/bin/env python  
# -*- coding:utf-8 -*-  

import datetime
import logging
import typing as t

from common.errors import ServiceError
from extensions.ext_db import db
from models.dao.dataset import DatasetDao
from models.dataset import Dataset
from models.file import UploadFile

logger = logging.getLogger("service")


class DatasetService(object):

    @classmethod
    def create_dataset(cls,
                       account_id: str = "",
                       name: str = "",
                       description: t.Optional[str] = None,
                       configs: t.Optional[t.Dict] = None) -> Dataset:
        """创建数据集

        Args:
            account_id: 当前用户id
            name: 数据集名称
            description: 数据集描述
            configs: 数据集配置

        Returns:

        """
        logger.debug(f"create_dataset: {account_id=}, {name=}, {description=}, {configs=}")
        dataset_is_exists = DatasetDao.dataset_is_exists(account_id=account_id, name=name)
        if dataset_is_exists:
            raise ServiceError(f"数据集名称: {name} 已存在")
        else:
            dataset = DatasetDao.create_dataset(account_id=account_id, name=name, description=description,
                                                configs=configs)
            return dataset

    @classmethod
    def get_all_dataset(cls, account_id: str = "") -> t.List[Dataset]:
        """获取所有数据集

        Args:
            account_id: 当前用户id

        Returns:

        """
        logger.debug(f"get_all_dataset: {account_id=}")
        datasets = DatasetDao.get_all_dataset(account_id=account_id)
        return datasets

    @classmethod
    def get_dataset_by_id(cls, account_id: str = "", dataset_id: str = "") -> Dataset:
        """获取数据集

        Args:
            account_id(str): 用户ID
            dataset_id(str): 数据集ID

        Returns:

        """
        logger.debug(f"get_all_dataset: {account_id=}, {dataset_id=}")
        dataset = DatasetDao.get_dataset(dataset_id=dataset_id, account_id=account_id)
        if dataset:
            return dataset
        else:
            raise ServiceError("数据集不存在")

    @classmethod
    def update_dataset(cls,
                       account_id: str = "",
                       dataset_id: str = "",
                       name: str = "",
                       description: t.Optional[str] = None,
                       configs: t.Optional[t.Dict] = None,
                       ) -> Dataset:
        """更新数据集

        Args:
            account_id(str): 用户ID
            dataset_id(str): 数据集ID
            name(str): 数据集名称
            description(str): 数据集描述
            configs(dict): 数据集配置

        Returns:

        """
        logger.debug(f"update_dataset: {account_id=}, {dataset_id=}, {name=}, {description=}, {configs=}")
        dataset = DatasetDao.get_dataset(dataset_id=dataset_id, account_id=account_id)

        if dataset:
            exists_datasets = db.session.query(Dataset) \
                .filter(Dataset.id != dataset_id) \
                .filter(Dataset.account_id == account_id) \
                .filter(Dataset.name == name) \
                .filter(Dataset.deleted == False) \
                .first()
            if exists_datasets:
                raise ServiceError(f"数据集名称: {name} 已存在")
            else:
                dataset = DatasetDao.update_dataset(dataset=dataset, name=name, description=description,
                                                    configs=configs)
                return dataset
        else:
            raise ServiceError("数据集不存在")

    @staticmethod
    def delete_dataset(dataset_id: str = "", account_id: str = ""):
        """删除数据集

        Args:
            dataset_id(str): 数据集ID
            account_id(str): 用户ID

        Returns:
        """
        dataset = DatasetDao.get_dataset(dataset_id=dataset_id, account_id=account_id)
        if dataset:
            dataset.deleted = True
            dataset.updated_at = datetime.datetime.utcnow()
            db.session.commit()
        else:
            logger.error(f"删除数据集失败, 数据集不存在. {dataset_id=}, {account_id=}")
            raise ServiceError("删除数据集失败, 数据集不存在. ")
