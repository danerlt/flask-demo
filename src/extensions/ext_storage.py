#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@desc: 存储相关
"""
import io
import logging
import os
import shutil
import typing as t
from pathlib import Path
from abc import ABC, abstractmethod

from minio import Minio
from minio.error import S3Error

from common.config import config, Config
from common import const

logger = logging.getLogger("run")


class Storage(ABC):

    @abstractmethod
    def __init__(self, cfg: Config):
        pass

    @abstractmethod
    def save(self, filename: str, data: t.AnyStr):
        pass

    def load(self, filename: str, stream: bool = False) -> t.Union[bytes, t.Generator]:
        if stream:
            return self.load_stream(filename)
        else:
            return self.load_once(filename)

    @abstractmethod
    def load_once(self, filename: str):
        pass

    def load_stream(self, filename: str) -> t.Generator:
        return self.generate(filename)

    @abstractmethod
    def generate(self, filename: str) -> t.Generator:
        pass

    @abstractmethod
    def download(self, filename: str, target_filepath: t.Union[str, Path]):
        pass

    @abstractmethod
    def exists(self, filename) -> bool:
        pass

    @abstractmethod
    def delete(self, filename: str):
        pass


class LocalStorage(Storage):
    def __init__(self, cfg: Config):
        self.storage_type = cfg.STORAGE_TYPE
        if self.storage_type != "local":
            raise Exception("STORAGE_TYPE must be local")
        self.folder = cfg.STORAGE_LOCAL_PATH
        if not os.path.isabs(self.folder):
            self.folder = os.path.join(const.ROOT_PATH.as_posix(), self.folder)

    def save(self, filename: str, data: t.AnyStr):
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename

        folder = os.path.dirname(filename)
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(os.getcwd(), filename), "wb") as f:
            f.write(data)

    def load_once(self, filename: str) -> bytes:
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename

        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        with open(filename, "rb") as f:
            data = f.read()

        return data

    def generate(self, file_name: str) -> t.Generator:
        if not self.folder or self.folder.endswith('/'):
            file_name = self.folder + file_name
        else:
            file_name = self.folder + '/' + file_name

        if not os.path.exists(file_name):
            raise FileNotFoundError("File not found")

        with open(file_name, "rb") as f:
            while chunk := f.read(4096):  # Read in chunks of 4KB
                yield chunk

    def download(self, filename: str, target_filepath: t.Union[str, Path]):
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename

        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        shutil.copyfile(filename, target_filepath)

    def exists(self, filename) -> bool:
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename

        return os.path.exists(filename)

    def delete(self, filename: str):
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename
        if os.path.exists(filename):
            os.remove(filename)


class MinioStorage(Storage):
    def __init__(self, cfg: Config):
        self.storage_type = cfg.STORAGE_TYPE
        if self.storage_type != "minio":
            raise Exception("STORAGE_TYPE must be minio")

        self.bucket_name = cfg.STORAGE_BUCKET
        self.client = Minio(cfg.SOTRAGE_ENTPOINT,
                            access_key=cfg.STORAGE_ACCESS_KEY,
                            secret_key=cfg.STORAGE_SECRET_KEY,
                            secure=cfg.STORAGE_SECURE)
        # 如果存储桶不存在则创建
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def save(self, filename: str, data: t.AnyStr):
        try:
            self.client.put_object(self.bucket_name, filename, io.BytesIO(data), len(data))
        except Exception as e:
            logger.error(f"minio put_object Error: {e}")
            raise e

    def load_once(self, filename: str) -> bytes:
        try:
            self.check(filename)
            data = self.client.get_object(self.bucket_name, filename)
            return data.read()
        except Exception as e:
            logger.error(f"minio get_object Error: {e}")
            raise e

    def generate(self, filename: str) -> t.Generator:
        try:
            data = self.client.get_object(self.bucket_name, filename)
            for d in data.stream(1 * 1024):
                yield d
        except Exception as e:
            logger.error(f"minio get_object Error: {e}")
            raise e

    def download(self, filename: str, target_filepath: t.Union[str, Path]):
        try:
            self.client.fget_object(self.bucket_name, filename, target_filepath)
        except Exception as e:
            logger.error(f"minio fget_object Error: {e}")
            raise e

    def exists(self, filename) -> bool:
        try:
            self.client.stat_object(self.bucket_name, filename)
            return True
        except Exception as e:
            logger.error(f"minio stat_object Error: {e}")
            return False

    def delete(self, filename: str):
        try:
            self.client.remove_object(self.bucket_name, filename)
        except Exception as e:
            logger.error(f"Error: {e}")
            raise e

    def check(self, filename: str):
        is_exists = self.exists(filename)
        if not is_exists:
            raise FileNotFoundError(f"File {filename} not found")


class StorageFactory(object):
    def __init__(self):
        self.storage_type = None
        self.storage = None

    def get_storage(self, cfg: Config):
        storage_type = cfg.STORAGE_TYPE
        self.storage_type = storage_type
        if self.storage_type == "local":
            self.storage = LocalStorage(cfg)
        elif self.storage_type == "minio":
            self.storage = MinioStorage(cfg)
        else:
            raise Exception(f"Unsupported STORAGE_TYPE: {self.storage_type}")
        return self.storage


storage_factory = StorageFactory()
storage = storage_factory.get_storage(config)
