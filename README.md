# flask-demo

flask-web项目模板

## 使用Docker-compose启动说明

### 构建镜像

进入到`docker`目录下，执行下面的命令构建镜像

```bash
docker-compose build
```

根据实际情况修改`docker`目录下的`ka-api.env`中的配置，然后执行下面的命令启动服务：

```bash
docker-compose up -d
```

查看日志：

```bash
docker-compose logs -f flask-demo
# 或者查看 logs/flask-demo 目录下的日志，如
tail -f logs/flask-demo/app.log
```

如果启动服务之后调用接口报错`401 Unauthorized: Access token is invalid`，可能是数据库`admin`用户未创建成功，可以进入容器手动创建：

```bash
# 进入容器
docker exec -it flask-demo-container bash
# 创建管理员账号 按照需要设置对应的参数，下面是一个示例
flask create-admin --name admin --password admin123 --token ka-admin123
```

## 本地启动说明

1. 复制 `.env-template` 文件为 `.env` 中
2. 修改 `.env` 中的 `SECRET_KEY` 为随机字符串，例如.

   ```bash
   openssl rand -base64 42
   ```

   根据实际情况设置其他配置项。

3. 使用 conda 创建一个名为 `flask-demo` 的环境

   ```bash
   conda create --name flask-demo python=3.10
   conda activate flask-demo
   ```

4. 安装依赖

   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

5. 升级数据库

   在首次启动之前，请将数据库迁移到最新版本。

   ```bash
   flask db upgrade
   ```

6. 启动服务:

   ```bash
   flask run --host 0.0.0.0 --port=5001 --debug
   ```

### 数据库初始化

具体看查看 [数据库初始化](src/migrations/README.md)

#### 创建管理员账户

命令说明：

```bash
$ flask create-admin --help
Usage: flask create-admin [OPTIONS]
                                   
  创建或更新管理员账户             
                                   
Options:                           
  --name TEXT      管理员用户名
  --password TEXT  管理员密码
  --help           Show this message and exit.

```

示例，创建一个名为 `admin` 的管理员账户，密码为 `admin123`

```bash
flask create-admin --name admin --password admin123
```

## 项目目录说明

```bash
├── build             # docker构建相关
├── docker            # docker-compose相关配置文件
├── run               # 服务运行相关
├── .env-template     # 环境变量模板
├── README.md         # Readme
├── src               # 源码目录
|  ├── commands       # flask 命令相关
|  ├── common         # 公共目录
|  ├── controllers    # 接口相关目录
|  ├── core           # 核心组件目录
|  ├── docker         # docker启动脚本目录
|  ├── extensions     # flask 扩展目录
|  ├── fields         # 接口字段目录
|  ├── migrations     # 数据库迁移目录
|  ├── models         # 数据库model目录
|  ├── services       # 业务逻辑目录
|  └── utils          # 工具类目录
└── tests             # 测试目录

```
