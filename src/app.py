#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@desc: flask app相关
"""
import sys
import logging
import os

# 将src路径加入到path中
sys.path.append(os.path.dirname(__file__))

if not os.environ.get("DEBUG") or os.environ.get("DEBUG").lower() != "true":
    from gevent import monkey

    monkey.patch_all()
    import grpc.experimental.gevent

    grpc.experimental.gevent.init_gevent()


import json
import time
import warnings

from werkzeug.exceptions import Unauthorized
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

from common.config import config
from commands.register import register_commands
from extensions import (ext_celery, ext_db, ext_migrate)
from extensions.ext_db import db
from extensions.ext_login import login_manager
from services.account_service import AccountService
from utils.log_utils import init_loggers
# 下面这个不能移除，否则执行flask db命令会有问题
from models import dataset

# 初始化日志
init_loggers()

logger = logging.getLogger("run")

warnings.simplefilter("ignore", ResourceWarning)

# fix windows platform
if os.name == "nt":
    os.system('tzutil /s "UTC"')
else:
    os.environ["TZ"] = "UTC"
    time.tzset()


class FlaskApp(Flask):
    pass


# ----------------------------
# Application Factory Function
# ----------------------------


def create_app() -> Flask:
    flask_app = FlaskApp(__name__)

    flask_app.config.from_object(config)

    flask_app.secret_key = flask_app.config["SECRET_KEY"]

    initialize_extensions(flask_app)
    register_blueprints(flask_app)
    register_commands(flask_app)

    return flask_app


def initialize_extensions(flask_app):
    # 由于现在已创建 Flask App 实例，因此将其传递给每个 Flask 扩展，以将其绑定到 Flask app
    ext_celery.init_app(flask_app)
    ext_db.init_app(flask_app)
    ext_migrate.init(flask_app, db)


# register blueprint routers
def register_blueprints(flask_app):
    from controllers import api_bp
    CORS(api_bp,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"]
         )
    flask_app.register_blueprint(api_bp)


# Flask-Login configuration
@login_manager.request_loader
def load_user_from_request(request_from_flask_login):
    """Load user based on the request."""
    # TODO 当用户登录之后需要考虑 token 的处理，暂时只考虑 apikey 的情况
    apikey = request_from_flask_login.args.get("apikey")
    if apikey:
        account_id = AccountService.verify(apikey)
        user_account = AccountService.load_user(account_id)
        return user_account
    else:
        raise Unauthorized("Invalid Authorization token.")


@login_manager.unauthorized_handler
def unauthorized_handler():
    """Handle unauthorized requests."""
    return Response(json.dumps({
        "code": "401",
        "status": "failure",
        "message": "Unauthorized."
    }), status=401, content_type="application/json")


# create app
app = create_app()
# 定义celery应用
celery = app.extensions["celery"]

if app.config["TESTING"]:
    print("App is running in TESTING mode")


@app.route("/health")
def health():
    res = {"code": 0, "msg": "success", "result": "ok"}
    return jsonify(res)


@app.route("/db-pool-stat")
def pool_stat():
    engine = db.engine
    res = {
        "pool_size": engine.pool.size(),
        "checked_in_connections": engine.pool.checkedin(),
        "checked_out_connections": engine.pool.checkedout(),
        "overflow_connections": engine.pool.overflow(),
        "connection_timeout": engine.pool.timeout(),
        "recycle_time": engine.pool._recycle
    }
    return res


# app hooks
ignore_urls = ["/health", "/db-pool-stat"]


@app.before_request
def log_before_request():
    """每次请求接口之前处理
    """
    try:
        url = request.path
        # 忽略部分URL
        for ignore_url in ignore_urls:
            if ignore_url in url:
                return
        method = request.method
        logger.debug(f"开始HTTP {method} 请求, url: {url}")
    except Exception as e:
        logger.warning(f"before_request error: {str(e)}")


@app.after_request
def process_request(response):
    def process_data():
        if isinstance(data, dict):
            if "code" in data and "msg" in data and "result" in data and data.get("code") != 0:
                return response
            else:
                res = {"code": 0, "msg": "success", "result": data}
                return jsonify(res)
        else:
            res = {"code": 0, "msg": "success", "result": data}
            return jsonify(res)

    try:
        if response.status_code == 200:
            url = request.path
            # 忽略部分URL
            for ignore_url in ignore_urls:
                if ignore_url in url:
                    return response

            if response.is_json:
                data = response.json
                processed_response = process_data()
                return processed_response
            else:
                res_data = response.get_data(as_text=True)
                try:
                    data = json.loads(res_data)
                    processed_response = process_data()
                    return processed_response
                except Exception:
                    logger.warning("precess_request return type is not json")
                    return response
        else:
            return response
    except Exception as e:
        logger.warning(f"process_request error: {str(e)}")
        return response


@app.errorhandler(Exception)
def process_error(e):
    logger.error(e)
    response = {"code": getattr(e, "code", 500), "msg": f"{str(e)}", "result": None}
    return jsonify(response), 200


@app.after_request
def log_after_request(response):
    """每次请求接口之前处理
    """
    try:
        url = request.path
        # 忽略部分URL
        for ignore_url in ignore_urls:
            if ignore_url in url:
                return response
        method = request.method
        logger.debug(f"结束HTTP {method} 请求, url: {url}")
    except Exception as e:
        logger.warning(f"after_request error: {str(e)}")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=False)
