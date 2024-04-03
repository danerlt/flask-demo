import logging

from flask_restful import reqparse, marshal

from common.errors import ParamsException, ApiException, ServiceError
from controllers.warps import ApiResource
from fields.dataset_fields import dataset_fields
from services.dataset_service import DatasetService

logger = logging.getLogger("api")


def _validate_name(name):
    if not name or len(name) < 1 or len(name) > 255:
        raise ValueError("Name must be between 1 to 255 characters.")
    return name


class DatasetsApi(ApiResource):

    def get(self, account_id):
        try:
            datasets = DatasetService.get_all_dataset(account_id=account_id)
            return marshal(datasets, dataset_fields)
        except ServiceError as e:
            logger.exception(f"获取数据集错误, error: {str(e)}")
            raise ApiException(e.msg)
        except Exception as e:
            logger.exception(f"获取数据集错误, error: {str(e)}")
            raise ApiException("获取数据集错误")

    def post(self, account_id):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("name", nullable=False, required=True,
                                help="type is required. Name must be between 1 to 40 characters.",
                                type=_validate_name)
            parser.add_argument("description", nullable=True, required=False, default='')
            parser.add_argument("configs", type=dict, nullable=True, required=False, default=None)
            args = parser.parse_args()
        except Exception as e:
            logger.exception(f"创建数据集参数解析错误, error: {str(e)}")
            raise ParamsException("创建数据集参数解析错误")
        try:
            name = args.get("name")
            description = args.get("description")
            configs = args.get("configs")
            dataset = DatasetService.create_dataset(account_id=account_id,
                                                    name=name,
                                                    description=description,
                                                    configs=configs)
            return marshal(dataset, dataset_fields)
        except ServiceError as e:
            logger.exception(f"创建数据集错误, error: {str(e)}")
            raise ApiException(e.msg)
        except Exception as e:
            logger.exception(f"创建数据集错误, error: {str(e)}")
            raise ApiException("创建数据集错误")


class DatasetApi(ApiResource):
    def get(self, account_id, dataset_id):
        try:
            dataset_id = str(dataset_id)
            dataset = DatasetService.get_dataset_by_id(account_id=account_id, dataset_id=dataset_id)
            return marshal(dataset, dataset_fields)
        except ServiceError as e:
            logger.exception(f"获取数据集错误, error: {str(e)}")
            raise ApiException(e.msg)
        except Exception as e:
            logger.exception(f"获取数据集错误, error: {str(e)}")
            raise ApiException("获取数据集错误")

    def delete(self, account_id, dataset_id):
        try:
            dataset_id = str(dataset_id)
            DatasetService.delete_dataset(account_id=account_id, dataset_id=dataset_id)
        except ServiceError as e:
            logger.exception(f"删除数据集错误, error: {str(e)}")
            raise ApiException(e.msg)
        except Exception as e:
            logger.exception(f"删除数据集错误, error: {str(e)}")
            raise ApiException("删除数据集错误")

    def put(self, account_id, dataset_id):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("name", nullable=False, required=True,
                                help="type is required. Name must be between 1 to 40 characters.",
                                type=_validate_name)
            # 注意 这里默认值要为None，否则不传字段会将原有的值清空。
            parser.add_argument("description", nullable=True, required=False, default=None)
            parser.add_argument("configs", type=dict, nullable=True, required=False, default=None)
            args = parser.parse_args()
        except Exception as e:
            logger.exception(f"更新数据集参数解析错误, error: {str(e)}")
            raise ParamsException("更新数据集参数解析错误")
        try:
            dataset_id = str(dataset_id)
            name = args.get("name")
            description = args.get("description")
            configs = args.get("configs")
            # TODO 这里需要考虑 如果不传入description字段，就不修改对应的字段，如何实现，不能将字段清空了。
            dataset = DatasetService.update_dataset(account_id=account_id,
                                                    dataset_id=dataset_id,
                                                    name=name,
                                                    description=description,
                                                    configs=configs)
            return marshal(dataset, dataset_fields)
        except ServiceError as e:
            logger.exception(f"更新数据集错误, error: {str(e)}")
            raise ApiException(e.msg)
        except Exception as e:
            logger.exception(f"更新数据集错误, error: {str(e)}")
            raise ApiException("更新数据集错误")



