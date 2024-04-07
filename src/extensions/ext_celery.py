#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@desc: celery 拓展
"""
from celery import Celery, Task
from flask import Flask


def init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(
        app.name,
        task_cls=FlaskTask,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_BACKEND"],
        task_ignore_result=True,
    )

    # Add SSL options to the Celery configuration
    ssl_options = {
        "ssl_cert_reqs": None,
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }

    celery_app.conf.update(
        result_backend=app.config["CELERY_RESULT_BACKEND"],
    )

    if app.config["BROKER_USE_SSL"]:
        celery_app.conf.update(
            broker_use_ssl=ssl_options,  # Add the SSL options to the broker configuration
        )

    # Make this the default app for all threads.
    celery_app.set_default()
    app.extensions["celery"] = celery_app

    # 启动默认的定时任务
    # TODO
    # imports = [
    #     "schedule.xxxx_task",  # 这个是python模块名称
    # ]
    #
    # beat_schedule = {
    #     'xxxx_task': {
    #         'task': 'schedule.xxxx_task.xxxx_task_func', # 这个是对应的task函数名
    #         'schedule': timedelta(days=7),
    #     },
    # }
    # celery_app.conf.update(
    #     beat_schedule=beat_schedule,
    #     imports=imports
    # )

    return celery_app
