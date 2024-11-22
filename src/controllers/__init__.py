from flask import Blueprint

from utils.external_api import ExternalApi

api_bp = Blueprint('api', __name__, url_prefix='/v1')
api = ExternalApi(api_bp)

# 导入接口相关模块，这里一定要写在 api 初始化后面，不然会报循环导入的错误
from controllers.dataset import DatasetsApi, DatasetApi

# 设置 URL map
api.add_resource(DatasetsApi, "/datasets")
api.add_resource(DatasetApi, "/datasets/<uuid:dataset_id>")
