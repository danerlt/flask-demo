#!/usr/bin/env python  
# -*- coding:utf-8 -*-  

import base64
import secrets

import click
from extensions.ext_db import db
from models.account import Account, AccountStatus, AccountRoleJoin, AccountRole, ApiToken
from utils.password import hash_password, password_pattern, valid_password, compare_password


@click.command('create-admin', help='创建或更新管理员账户')
@click.option('--name', default='admin', help='管理员用户名')
@click.option('--password', default='admin123', help='管理员密码')
@click.option('--token', default='admin123', help='管理员API token')
def create_admin_cmd(name, password, token):
    # 判断 admin 账户是否存在
    admin_account = db.session.query(Account).filter(Account.name == name).one_or_none()
    if admin_account:
        # admin 账户存在，更新
        click.echo(click.style('Admin account exists. Updating', fg='yellow'))
        if not compare_password(password, admin_account.password, admin_account.password_salt):
            # 密码没变不需要更新密码
            pass
        else:
            # 密码变了，需要更新密码
            try:
                valid_password(password)
            except Exception:
                click.echo(click.style('Sorry, the passwords must match {}'.format(password_pattern), fg='red'))
                return
            # generate password salt
            salt = secrets.token_bytes(16)
            base64_salt = base64.b64encode(salt).decode()
            # encrypt password with salt
            password_hashed = hash_password(password, salt)
            base64_password_hashed = base64.b64encode(password_hashed).decode()
            admin_account.password = base64_password_hashed
            admin_account.password_salt = base64_salt

        # 判断是否需要新增 API token
        api_token = db.session.query(ApiToken) \
            .filter(ApiToken.account_id == admin_account.id) \
            .filter(ApiToken.token == token) \
            .one_or_none()
        if not api_token:
            # 没有对应的 API Token，新增 API token
            api_token = ApiToken(account_id=admin_account.id, token=token)
            db.session.add(api_token)

        # 提交事务
        db.session.commit()
        click.echo(click.style('Admin account has been updated successfully!', fg='green'))
    else:
        # admin 账户不存在，新建
        click.echo(click.style('Admin account does not exist. Creating...', fg='yellow'))
        salt = secrets.token_bytes(16)
        base64_salt = base64.b64encode(salt).decode()

        # encrypt password with salt
        password_hashed = hash_password(password, salt)
        base64_password_hashed = base64.b64encode(password_hashed).decode()
        admin_account = Account(name=name,
                                password=base64_password_hashed,
                                password_salt=base64_salt,
                                status=AccountStatus.ACTIVED.value,
                                initialized_at=db.func.now(),
                                )
        db.session.add(admin_account)

        # create or update account role join
        account_role_join = db.session.query(AccountRoleJoin) \
            .filter(AccountRoleJoin.account_id == admin_account.id) \
            .one_or_none()
        if account_role_join:
            account_role_join.role = AccountRole.ADMIN.value
        else:
            account_role_join = AccountRoleJoin(account_id=admin_account.id, role=AccountRole.ADMIN.value)
            db.session.add(account_role_join)

        # create api token
        api_token = ApiToken(account_id=admin_account.id, token=token)
        db.session.add(api_token)

        db.session.commit()
        click.echo(click.style('Admin account has been created successfully!', fg='green'))
