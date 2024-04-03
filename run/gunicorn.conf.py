#!/usr/bin/env python  
# -*- coding:utf-8 -*-  

import multiprocessing

# 获取CPU核数，with这个是读取docker容器中的配置
try:
    with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") as f:
        quota = int(f.read())
        if quota > 0:
            cores = quota // 100000
        else:
            cores = multiprocessing.cpu_count()
except Exception as e:
    print(e)
    cores = multiprocessing.cpu_count()

# 设置workers 通常可以设置成CPU核数*2或者4+1
# 具体设置那个比较好可以做压力测试来判断
workers = cores * 2 + 1

# worker_class 默认是 sync， 使用单进程，对性能要求不高可以使用。
# 设置 thread 参数，会自动将 worker_class 设置成 gthread，这个是使用的线程池，当 gevent 无法使用的时候可以使用这个。
# eventlet 库用的人比较少，且 eventlet 官方推荐直接使用asynio，故这个也不推荐使用。
# 使用 Meinheld 代替 gevent， 这个性能更好，但是安装需要编译，比较麻烦，而且这个项目很久没有维护了，不推荐使用。
# worker_class = "meinheld.gmeinheld.MeinheldWorker"
# gevent 可以提供异步支持，对 Flask 框架来说，Flask 框架本身对异步的支持不是很好，如果对异步要求很高，可以换成 fastapi 框架 + uvicorn 框架，不使用Gunicorn
worker_class = "gevent"
keeplive = 10
timeout = 60
preload_app = True
reload = True
x_forwarded_for_header = "X_FORWARDED_FOR"

print(f"{workers=}, {worker_class}")
