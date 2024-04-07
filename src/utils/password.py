#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
import binascii
import hashlib
import re

# 密码必须至少8个字符长，且至少包含一个字母和一个数字
# (?=.*[a-zA-Z])：密码必须至少包含一个字母。这是通过正向肯定预查（positive lookahead）完成的，即密码后面（.*）必须跟着至少一个字母（[a-zA-Z]）。
# (?=.*\d)：密码必须至少包含一个数字。这也是通过正向肯定预查完成的，即密码后面（.*）必须跟着至少一个数字（\d）。
# .{8,}：密码必须至少包含8个字符。这是通过限定符（quantifier）完成的，即任意字符（.）必须出现至少8次（{8,}）。
password_pattern = r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$"


def valid_password(password: str):
    """校验密码

    如果密码正则校验不通过就抛错，校验通过就返回密码字符串
    """
    # 密码正则表达式
    pattern = password_pattern
    # Check if the password matches the pattern
    if re.match(pattern, password) is not None:
        return password

    raise ValueError('Not a valid password.')


def hash_password(password_str: str, salt_byte: bytes) -> bytes:
    """对密码进行哈希处理

    Args：
        password_str (str): 待哈希处理的密码字符串
        salt_byte (bytes): 用于增加密码哈希难度的盐值（字节类型）

    Returns：
        bytes: 哈希处理后的密码

    """
    dk = hashlib.pbkdf2_hmac('sha256', password_str.encode('utf-8'), salt_byte, 10000)
    return binascii.hexlify(dk)


def compare_password(password_str: str, password_hashed_base64: bytes, salt_base64: bytes) -> bool:
    """比较密码是否匹配

    Args:
        password_str (str): 待比较的密码
        password_hashed_base64 (bytes): 哈希后的密码（base64解码后）
        salt_base64 (bytes): 盐值（base64解码后）

    Returns:
        bool: 如果密码匹配返回True，否则返回False
    """
    # compare password for login
    return hash_password(password_str, base64.b64decode(salt_base64)) == base64.b64decode(password_hashed_base64)
