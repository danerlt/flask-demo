#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@desc: 账户相关数据库表
"""

import enum

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

from extensions.ext_db import db
from utils.helper import generate_string


class AccountStatus(str, enum.Enum):
    """账户状态"""
    UNACTIVED = "unactived"  # 未激活 一般需要通过邮件验证来激活
    ACTIVED = "actived"  # 已激活
    BANNED = "banned"  # 已禁用
    CLOSED = "closed"  # 已注销


class Account(UserMixin, db.Model):
    __tablename__ = "accounts"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="account_pkey"),  # 主键
        db.UniqueConstraint("name", name="account_name_idx")  # 唯一索引 name 字段
    )

    # nullable设置为True，这一列可以包含null值。将nullable设置为False，这一列不可以包含null值，每一条记录都必须为这一列提供一个值
    id = db.Column(UUID, server_default=db.text("uuid_generate_v4()"), comment="用户ID")
    name = db.Column(db.String(255), nullable=False, comment="用户名")
    email = db.Column(db.String(255), nullable=True, comment="邮箱")
    password = db.Column(db.String(255), nullable=True, comment="密码")
    password_salt = db.Column(db.String(255), nullable=True, comment="密码salt")
    last_login_at = db.Column(db.DateTime, nullable=True, comment="上次登录时间")
    last_login_ip = db.Column(db.String(255), nullable=True, comment="上次登录IP")
    status = db.Column(db.String(16), nullable=False, server_default=db.text("'actived'::character varying"), comment="账户状态")
    initialized_at = db.Column(db.DateTime, comment="账户初始化时间")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))

    @property
    def is_password_set(self):
        return self.password is not None

    def get_status(self) -> AccountStatus:
        status_str = self.status
        return AccountStatus(status_str)


class AccountRole(enum.Enum):
    """用户角色

    admin可以修改模型，提示词等
    normal就是普通用户，只能对数据集管理和对话
    """
    ADMIN = "admin"
    NORMAL = "normal"


class AccountRoleJoin(db.Model):
    """账户和角色关联表"""
    __tablename__ = "account_role_joins"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="account_role_pkey"),
        db.Index("account_role_join_account_id_idx", "account_id"),
    )

    id = db.Column(UUID, server_default=db.text("uuid_generate_v4()"), comment="账户和角色关联ID")
    account_id = db.Column(UUID, nullable=False, comment="账号ID")
    role = db.Column(db.String(16), nullable=False, server_default="normal", comment="角色")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))


class ApiToken(db.Model):
    __tablename__ = "api_tokens"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="api_token_pkey"),
        db.Index("api_token_token_idx", "token"),
        db.Index("api_token_account_idx", "account_id")
    )

    id = db.Column(UUID, server_default=db.text("uuid_generate_v4()"))
    account_id = db.Column(UUID, nullable=True)
    token = db.Column(db.String(255), nullable=False)
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))

    @staticmethod
    def generate_api_key(prefix, n):
        while True:
            result = prefix + generate_string(n)
            while db.session.query(ApiToken).filter(ApiToken.token == result).count() > 0:
                result = prefix + generate_string(n)

            return result
