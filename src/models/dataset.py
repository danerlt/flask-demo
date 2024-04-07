#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin
from sqlalchemy.dialects.postgresql import UUID

from extensions.ext_db import db

logger = logging.getLogger("run")


@dataclass
class SplitterConfig(DataClassJsonMixin):
    """
    Splitter配置数据类

    Args:
        splitter_name (str): splitter 名称
    """
    splitter_name: str


@dataclass
class RetrieverConfig(DataClassJsonMixin):
    """
    检索配置

    Args:
    """
    engine_name: str

@dataclass
class DatasetConfigs(DataClassJsonMixin):
    """
    数据集配置数据类

    Args:
        splitter (SplitterConfig): Splitter配置
        retriever (RetrieverConfig): Retriever配置
    """
    splitter: SplitterConfig
    retriever: RetrieverConfig
    
    
class Dataset(db.Model):
    """数据集表"""
    __tablename__ = "datasets"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="dataset_pkey"),
    )
    id = db.Column(UUID, server_default=db.text("uuid_generate_v4()"))
    account_id = db.Column(UUID, nullable=False, comment="用户ID")
    name = db.Column(db.String(255), nullable=False, comment="数据集名称")
    description = db.Column(db.Text, nullable=True, comment="数据集描述")
    configs = db.Column(db.JSON, nullable=True, comment="数据集配置")
    deleted = db.Column(db.Boolean, nullable=False, server_default=db.text("false"), comment="是否删除,默认为False")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    
    @classmethod
    def get_default_dataset_configs(cls) -> DatasetConfigs:
        """获取默认数据集配置

        Returns: 默认数据集配置(DatasetConfigs)

        """
        default_configs = DatasetConfigs(
            splitter=cls.get_default_splitter_config(),
            retriever=cls.get_default_retriever_config(),
        )
        return default_configs