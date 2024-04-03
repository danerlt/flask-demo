# base image
FROM python:3.10-slim-bookworm

LABEL maintainer="danerlt001@gmail.com"

# 使用 root 用户
USER root

# 设置环境变量
# 防止 python 将 pyc 文件写入硬盘
ENV PYTHONDONTWRITEBYTECODE 1
# 防止 python 缓冲 (buffering) stdout 和 stderr, 以便更容易地进行容器日志记录
ENV PYTHONUNBUFFERED 1
# 设置pip安装命令
ENV PIP_INSTALL="pip3 install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ "
# 设置时区
ENV TZ UTC

# 设置apt源
COPY build/sources.list /etc/apt/
# 安装apt依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends wget curl vim nginx \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*


# 拷贝python依赖
COPY build /build

# 安装python依赖
RUN  ${PIP_INSTALL} -r /build/requirements.txt

# 设置项目文件
WORKDIR /app

# 拷贝项目文件
COPY src /app
COPY run /app/run

# 设置nginx和清空日志
RUN rm /etc/nginx/sites-enabled/default \
    && cp /app/run/nginx.conf /etc/nginx/sites-available/app.conf \
    && mkdir -p /app/logs \
    && find /app/logs -name "*.log" -exec sh -c '> "{}"'   \;

EXPOSE 8000

CMD ["bash", "/app/run/start.sh"]

